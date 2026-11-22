"""A local decision service for SAG-Wiki's deep search (the Jev "systemone" protocol).

SAG-Wiki posts {"model", "state", "questions"}; `state` is a JSON string holding the original question and the
evidence kept so far, and each question asks whether one candidate passage is necessary evidence. We answer
{"answers": {name: {"type": "noul", "noul": p}}} with p in [0, 1] from a model running on this machine:

  ce:<path>         a cross-encoder reranker (sentence-transformers), p = its sigmoid score for (question, passage)
  qwen3rr:<path>    Qwen3-Reranker, p = P("yes") under its published prompt, with SAG-Wiki's criterion as the instruction
  d1:<path>         Liquid AI d1-2B, given SAG-Wiki's request unchanged through its own system_one() call
  hindsight:<path>  Hindsight hs-decide-1-flash, given the request unchanged through its own DecisionModel.answer()
  proxy:<url>       a decision model's own HTTP server on this machine (KnowLine's knowline_server.py), request unchanged

The first two are rerankers: they see only the question and one passage. The last three are decision models built
for this protocol: they also see the evidence SAG-Wiki has kept and the criterion it asks.

Every request and answer is appended to --log as one JSON line, so each score can be read afterwards.
Run: python decide.py --port 8700 --scorer ce:/path/to/model --log decisions.jsonl
"""
import argparse, json, math, threading, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def candidate_text(instr):
    parts = [instr.get("candidate_title", ""), instr.get("candidate_heading", ""), instr.get("candidate_passage", "")]
    return "\n".join(p for p in parts if p)


class CrossEncoderScorer:
    def __init__(self, path):
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(path, max_length=512)  # ponytail: passages past 512 tokens are cut, as the model was trained
        self.lock = threading.Lock()

    def __call__(self, question, state, items):
        with self.lock:
            scores = self.model.predict([(question, candidate_text(i)) for _, i in items], batch_size=32)
        return [1 / (1 + math.exp(-float(s))) for s in scores]  # these models return raw logits


class Qwen3RerankerScorer:
    PREFIX = ('<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct '
              'provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n')
    SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"

    def __init__(self, path):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(path, padding_side="left")
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16).to(dev).eval()
        self.yes, self.no = self.tok.convert_tokens_to_ids("yes"), self.tok.convert_tokens_to_ids("no")
        self.lock = threading.Lock()

    def __call__(self, question, state, items):
        criterion = items[0][1].get("question", "")
        texts = [f"{self.PREFIX}<Instruct>: {criterion}\n<Query>: {question}\n<Document>: {candidate_text(i)}{self.SUFFIX}"
                 for _, i in items]
        out = []
        with self.lock, self.torch.no_grad():
            for k in range(0, len(texts), 8):
                enc = self.tok(texts[k:k + 8], padding=True, truncation=True, max_length=8192, return_tensors="pt").to(self.model.device)
                logits = self.model(**enc).logits[:, -1, [self.no, self.yes]].float()
                out += self.torch.softmax(logits, dim=-1)[:, 1].tolist()
        return out


class D1Scorer:
    native = True

    def __init__(self, path):
        import torch, transformers.utils, transformers.utils.import_utils
        from transformers import AutoModel
        # Triton needs a C compiler to build its kernels and this machine has none; told Triton is absent, d1's own
        # code runs its short convolutions in plain PyTorch instead (integrations_lfm3.can_use_lfm3_conv)
        transformers.utils.is_triton_available = transformers.utils.import_utils.is_triton_available = lambda: False
        self.model = AutoModel.from_pretrained(path, trust_remote_code=True, dtype=torch.bfloat16).to("cuda").eval()
        self.lock = threading.Lock()

    def answer(self, payload):
        with self.lock:
            return self.model.system_one(payload["state"], payload["questions"])


class HindsightScorer:
    native = True

    def __init__(self, path):
        from hindsight_decision import DecisionModel
        self.model, self.lock = DecisionModel.from_pretrained(path), threading.Lock()

    def answer(self, payload):
        with self.lock:
            return self.model.answer({"state": payload["state"], "questions": payload["questions"]})


class ProxyScorer:
    native = True

    def __init__(self, url):
        self.url = url

    def answer(self, payload):
        # KnowLine's server takes at most 64 questions a request (MAX_QUESTIONS) and SAG-Wiki does not read its
        # refusal as a batch limit, so larger batches go in parts with the same state; each question is scored on its own
        names, answers = list(payload["questions"]), {}
        for k in range(0, len(names), 64):
            part = dict(payload, questions={n: payload["questions"][n] for n in names[k:k + 64]})
            req = urllib.request.Request(self.url, json.dumps(part).encode(), {"Content-Type": "application/json"})
            answers.update(json.load(urllib.request.urlopen(req, timeout=3600))["answers"])
        return {"answers": answers}


def make_scorer(spec):
    kind, _, arg = spec.partition(":")
    return {"ce": CrossEncoderScorer, "qwen3rr": Qwen3RerankerScorer, "d1": D1Scorer, "hindsight": HindsightScorer,
            "proxy": ProxyScorer}[kind](arg)


def answer(scorer, payload):
    if getattr(scorer, "native", False):
        return scorer.answer(payload)["answers"]
    items = [(name, q.get("instructions", {}), q.get("criteria", {})) for name, q in payload["questions"].items()]
    try:
        state = json.loads(payload.get("state") or "")
    except (TypeError, json.JSONDecodeError):
        state = None
    if not isinstance(state, dict):  # SAG-Wiki's connection test sends the plain string "Connection test"
        return {name: {"type": "noul", "noul": 1.0} for name, _, _ in items}
    question = state.get("original_question") or ""
    scores = scorer(question, state, [(n, i) for n, i, _ in items])
    return {name: {"type": "noul", "noul": min(1.0, max(0.0, s))} for (name, _, _), s in zip(items, scores)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8700)
    ap.add_argument("--scorer", required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    scorer, log_lock = make_scorer(a.scorer), threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            t = time.time()
            answers = answer(scorer, payload)
            body = json.dumps({"answers": answers}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            with log_lock, open(a.log, "a") as f:
                f.write(json.dumps({"t": t, "seconds": round(time.time() - t, 3), "request": payload, "answers": answers},
                                   ensure_ascii=False) + "\n")

        def log_message(self, *args):
            pass

    print(f"decide.py ready on 127.0.0.1:{a.port} with {a.scorer}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
