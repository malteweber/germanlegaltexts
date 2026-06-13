import pytest

from germanlegaltexts.model.Normverweis import Normverweis


@pytest.mark.parametrize(
    "raw, typ, einheit, qualifiers, gesetz",
    [
        # simple § with no qualifiers
        ("§ 212 StGB", "§", "212", {}, "StGB"),
        ("§ 433 BGB", "§", "433", {}, "BGB"),
        # § with Absatz
        ("§ 42 Abs 3 JGG", "§", "42", {"Abs": "3"}, "JGG"),
        # § with Abs + Satz
        ("§ 113 Abs 5 S 1 VwGO", "§", "113", {"Abs": "5", "S": "1"}, "VwGO"),
        # § with Abs + Satz + Nr
        ("§ 15a Abs 1 S 1 Nr 2 ZPOEG", "§", "15a", {"Abs": "1", "S": "1", "Nr": "2"}, "ZPOEG"),
        # § with Nr + Buchst
        ("§ 4 Nr 16 Buchst b UStG 1999", "§", "4", {"Nr": "16", "Buchst": "b"}, "UStG 1999"),
        # § with Halbsatz
        ("§ 160 Abs 2 Nr 3 Halbs 1 SGG", "§", "160", {"Abs": "2", "Nr": "3", "Halbs": "1"}, "SGG"),
        # § with Alternative
        ("§ 213 Alt 2 StGB", "§", "213", {"Alt": "2"}, "StGB"),
        # § with subparagraph letter suffix in einheit
        ("§ 87a BGB", "§", "87a", {}, "BGB"),
        # §§ range with ff suffix
        ("§§ 535ff BGB", "§§", "535ff", {}, "BGB"),
        # Artikel
        ("Art 267 AEUV", "Art", "267", {}, "AEUV"),
        ("Art 1 Abs 1 GG", "Art", "1", {"Abs": "1"}, "GG"),
        # Artikel with EU directive as gesetz
        ("Art 7 EGRL 46/95", "Art", "7", {}, "EGRL 46/95"),
        ("Art 130 Abs 1 EUV 2017/1001", "Art", "130", {"Abs": "1"}, "EUV 2017/1001"),
        # Richtlinie (R) prefix
        ("R 31 Abs 2 S 1 ErbStR 2003", "R", "31", {"Abs": "2", "S": "1"}, "ErbStR 2003"),
        # Teil with letter einheit and DBuchst qualifier
        (
            "Teil A Nr 3 Buchst e DBuchst ee VersMedV",
            "Teil", "A",
            {"Nr": "3", "Buchst": "e", "DBuchst": "ee"},
            "VersMedV",
        ),
        # gesetz carries SGB book number
        ("§ 112 Abs 2 S 1 Nr 1 SGB 5", "§", "112", {"Abs": "2", "S": "1", "Nr": "1"}, "SGB 5"),
        # gesetz carries state abbreviation
        ("§ 9 Abs 2 Nr 5 PersVG BW 2015", "§", "9", {"Abs": "2", "Nr": "5"}, "PersVG BW 2015"),
        # gesetz carries "vom <date>" suffix
        (
            "§ 31 Abs 1 S 1 BVG vom 21.06.2012",
            "§", "31",
            {"Abs": "1", "S": "1"},
            "BVG vom 21.06.2012",
        ),
        # double-space normalization
        ("§ 43 Abs 1 S 2  AMG", "§", "43", {"Abs": "1", "S": "2"}, "AMG"),
        # no typ marker — entire string becomes gesetz
        ("EStG VZ 2010", None, None, {}, "EStG VZ 2010"),
        ("GG", None, None, {}, "GG"),
        ("EGRL 46/95", None, None, {}, "EGRL 46/95"),
    ],
)
def test_from_string(raw, typ, einheit, qualifiers, gesetz):
    n = Normverweis.from_string(raw)
    assert n.raw == raw
    assert n.typ == typ
    assert n.einheit == einheit
    assert n.qualifiers == qualifiers
    assert n.gesetz == gesetz


def test_empty_string():
    n = Normverweis.from_string("")
    assert n.typ is None
    assert n.einheit is None
    assert n.qualifiers == {}
    assert n.gesetz == ""


def test_whitespace_only():
    n = Normverweis.from_string("   ")
    assert n.typ is None
    assert n.einheit is None
    assert n.qualifiers == {}
    assert n.gesetz == ""
