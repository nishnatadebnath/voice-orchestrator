"""Format parsed XML prompts into text suitable for an LLM."""


def format_prompt(prompt: dict[str, str]) -> str:
    """Convert prompt sections into a consistently formatted string."""
    sections = [
        ("Role", prompt.get("role", "")),
        ("Objective", prompt.get("objective", "")),
        ("Instructions", prompt.get("instructions", "")),
        ("Response Guidelines", prompt.get("response_guidelines", "")),
    ]

    # Include only sections that contain content.
    formatted_sections = [
        f"{title}:\n{content}"
        for title, content in sections
        if content.strip()
    ]

    return "\n\n".join(formatted_sections)