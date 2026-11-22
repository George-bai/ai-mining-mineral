"""Prompt templates transcribed from MineralBench Appendix A (Listings A-1..A-3).

The paper stores these as structured config files; the Executor module combines
System Prompt + Task Instruction + the sample task input into the model input.
Only A-2 (short answer, used by Mineral-Term and Mineral-Property) and A-3
(named entity recognition, used by Geo-NER) are needed for the three core
domain tasks. A-1 (single choice) is kept for completeness.
"""

SYSTEM_CHOICE = "You are a knowledgeable assistant."

USER_CHOICE = """Please give the correct answer to the following multiple-choice question:
Question: {question}
Options:
{options}
Requirements:
1. Output only one option label (A, B, C, D, ...), with no extra words.
2. Do not provide explanation or reasoning.
3. Do not fabricate an answer.
Please output the answer label directly (A, B, C, D, ...):"""

SYSTEM_SHORT = "You are a domain expert."

USER_SHORT = """Please provide a detailed, accurate, and academically rigorous answer with \
professional depth for the following short-answer question.
Strictly prohibit fabricating dates or numerical values. Ensure the answer is accurate and does \
not omit any key information.
Question:
{question}
Requirements:
1. Output only the core answer or term. Keep it concise without additional explanations.
2. Use rigorous academic phrasing and professional terminology.
3. Avoid phrases such as 'according to research' or 'literature indicates'; state facts and \
conclusions directly."""

SYSTEM_NER = "You are a domain expert in geology and mineral exploration."

USER_NER = """Instruction: Given the label set of entities, please recognize all the entities in the \
text. The answer format should be "{{type1: [entity1, entity2], type2: [entity3]}}". Below is an example.
Label Set: [MINERAL]
Text: [Quartz and feldspar are common]
Answer: [{{"MINERAL":["Quartz","Feldspar"]}}]
Label Set: {entity_type}
Text:{text}
Answer:[]"""

TASK_PROMPTS = {
    "Mineral-Term": (SYSTEM_SHORT, USER_SHORT, "question"),
    "Mineral-Property": (SYSTEM_SHORT, USER_SHORT, "question"),
    "Geo-NER": (SYSTEM_NER, USER_NER, "text"),
}


def build_messages(sample: dict, ner_cue: str = "paper") -> list[dict]:
    """Fill the task template with the sample's task input fields (paper Sec. 3.2/3.4).

    ner_cue="paper" reproduces Listing A-3 literally, ending with the `Answer:[]` cue.
    ner_cue="open" ends with a bare `Answer:` cue; used only as a sensitivity check, because the
    literal `[]` cue can prime models to emit empty entity lists.
    """
    system, user, _ = TASK_PROMPTS[sample["type"]]
    inp = sample["input"]
    if sample["type"] == "Geo-NER":
        entity_type = "[" + ", ".join(inp["entity_types"]) + "]"
        user = user.format(entity_type=entity_type, text=inp["text"])
        if ner_cue != "paper":
            user = user[: -len("Answer:[]")] + "Answer:"
    elif sample["type"] == "Mineral-Property":
        user = user.format(question=inp["question"])
    else:
        user = user.format(question=inp["question"])
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
