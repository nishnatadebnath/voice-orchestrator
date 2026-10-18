
import xml.etree.ElementTree as ET


def parse_prompt(xml_content: str) -> dict[str, str]:
    """Parse an XML prompt into a simple dictionary."""

    # Parse the XML string and obtain its root element.
    root = ET.fromstring(xml_content)

    # Require the expected root element to avoid silently accepting
    # an unrelated XML document.
    if root.tag != "prompt":
        raise ValueError("XML root element must be <prompt>")

    prompt_id = root.get("id")
    version = root.get("version")

    if not prompt_id or not version:
        raise ValueError("Prompt must have an id and version")

    # Extract prompt sections while preserving their readable text.
    sections = {}

    for section in root:
        sections[section.tag] = (section.text or "").strip()

    return {
        "id": prompt_id,
        "version": version,
        **sections,
    }
