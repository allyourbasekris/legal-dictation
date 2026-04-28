import logging, re

log = logging.getLogger("legal-dictation")


def _capitalize(text):
    return text[0].upper() + text[1:] if text else text


def _split_sentences(text):
    """Split transcript into sentences using natural pause markers from dictation."""
    # Split on pause markers that indicate sentence boundaries in dictation
    pauses = re.split(
        r'(?:(?:\.|\?|!)\s+)|'
        r'(?:\b(?:Okay|Right|So|Now|Next|Thanks|Thank you)\b[,.]?\s*)',
        text,
        flags=re.IGNORECASE,
    )
    sentences = []
    for p in pauses:
        p = p.strip()
        if p:
            p = _capitalize(p)
            if not p.endswith("."):
                p += "."
            sentences.append(p)
    return sentences


def _detect_sections(sentences):
    """Classify sentences into legal document sections based on keywords."""
    sections = {
        "FILE NOTES": [],
        "TIME RECORDING": [],
        "CORRESPONDENCE": [],
        "ACTION ITEMS": [],
        "OTHER": [],
    }

    current_section = "OTHER"
    for s in sentences:
        lower = s.lower()

        # Section transition keywords
        if "file note" in lower or "file note:" in lower:
            current_section = "FILE NOTES"
        elif re.search(r'\b(\d+k|£\d+|reimburse|expenses?|payment)\b', lower):
            current_section = "TIME RECORDING"
        elif re.search(r'\b(letter to|dear |write to|draft letter|enclosed?)\b', lower):
            current_section = "CORRESPONDENCE"
        elif re.search(r'\b(can you|please |need to|make sure|i want|we need|send|amend|pull out|copy and)\b', lower, re.IGNORECASE):
            current_section = "ACTION ITEMS"
        elif re.search(r'^(okay|right|so |now |next)', lower):
            # Transition word at start — keep in same section
            pass
        else:
            # Continue in current section for continuity
            pass

        sections[current_section].append(s)

    return sections


def process(text):
    """Post-process raw transcription: punctuation, capitalization, section formatting.

    Returns (corrected_text, formatted_text) — both strings.
    """
    log.info(f"Processing {len(text)} chars of transcription text")

    sentences = _split_sentences(text)
    corrected = " ".join(sentences)

    sections = _detect_sections(sentences)

    formatted_parts = []
    for header in ["FILE NOTES", "TIME RECORDING", "CORRESPONDENCE", "ACTION ITEMS"]:
        items = sections[header]
        if items:
            formatted_parts.append(f"=== {header} ===")
            if header == "ACTION ITEMS":
                for item in items:
                    formatted_parts.append(f"  [ ] {item}")
            else:
                for item in items:
                    formatted_parts.append(f"  - {item}")
            formatted_parts.append("")

    if sections["OTHER"]:
        formatted_parts.append("=== OTHER NOTES ===")
        for item in sections["OTHER"]:
            formatted_parts.append(f"  - {item}")

    formatted = "\n".join(formatted_parts).strip()

    log.info(f"Corrected: {len(corrected)} chars, Formatted: {len(formatted)} chars")
    return corrected, formatted
