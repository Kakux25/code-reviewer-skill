"""Stand-in: search/index.py lowercase tokenizer (CHG-103)."""
def tokenize(text):
    return text.lower().split()
