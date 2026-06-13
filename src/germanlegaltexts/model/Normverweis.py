from dataclasses import dataclass, field
import re


TYP_MARKERS = {"§", "§§", "Art", "R", "Teil"}
QUALIFIER_KEYS = {"Abs", "S", "Nr", "Halbs", "Alt", "Buchst", "DBuchst"}


@dataclass
class Normverweis:
    """A single structured citation of a German legal norm.

    Example: "§ 4 Nr 16 Buchst b UStG 1999" →
        typ="§", einheit="4",
        qualifiers={"Nr": "16", "Buchst": "b"},
        gesetz="UStG 1999"
    """
    raw: str
    typ: str | None
    einheit: str | None
    qualifiers: dict[str, str] = field(default_factory=dict)
    gesetz: str = ""

    @classmethod
    def from_string(cls, raw: str) -> "Normverweis":
        text = re.sub(r"\s+", " ", raw).strip()
        tokens = text.split(" ") if text else []

        typ: str | None = None
        einheit: str | None = None
        qualifiers: dict[str, str] = {}
        i = 0

        if tokens and tokens[0] in TYP_MARKERS:
            typ = tokens[0]
            i = 1
            if i < len(tokens):
                einheit = tokens[i]
                i += 1

        while i + 1 < len(tokens) and tokens[i] in QUALIFIER_KEYS:
            qualifiers[tokens[i]] = tokens[i + 1]
            i += 2

        gesetz = " ".join(tokens[i:])

        return cls(
            raw=raw,
            typ=typ,
            einheit=einheit,
            qualifiers=qualifiers,
            gesetz=gesetz,
        )
