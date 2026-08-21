def extract_page_facts(text: str) -> dict:
    return {"text_length": len(text), "has_dates": any(char.isdigit() for char in text)}

