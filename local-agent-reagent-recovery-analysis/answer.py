"""Print an attempt's tool calls and final answer from Pi's event stream, for reading beside the key."""
import json, sys

calls, text = [], ""
for line in open(sys.argv[1]):
    e = json.loads(line)
    if e.get("type") == "tool_execution_start":
        calls.append(f"- `{e.get('toolName')}` {json.dumps(e.get('args'), ensure_ascii=False)[:400]}")
    elif e.get("type") == "message_end" and e.get("message", {}).get("role") == "assistant":
        t = "".join(c.get("text", "") for c in e["message"]["content"] if c.get("type") == "text").strip()
        text = t or text
print("## Tool calls\n\n" + "\n".join(calls) + "\n\n## Answer\n\n" + text)
