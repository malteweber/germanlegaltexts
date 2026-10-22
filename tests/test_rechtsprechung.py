import pytest
from germanlegaltexts.model.Rechtsprechung import Rechtsprechung, RIIIndexItem


def test_rii_index_item_creation():
    """Test creating an RIIIndexItem."""
    item = RIIIndexItem(
        gericht="BGH 9. Zivilsenat",
        entsch_datum="20100114",
        aktenzeichen="IX ZB 72/08",
        link="http://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-JURE100055033.zip",
        modified="2025-06-23T21:55:54.378Z"
    )
    
    assert item.gericht == "BGH 9. Zivilsenat"
    assert item.entsch_datum == "20100114"
    assert item.aktenzeichen == "IX ZB 72/08"
    assert item.link.endswith(".zip")


def test_rechtsprechung_from_xml(sample_judgement_xml):
    """Test parsing a Rechtsprechung from XML."""
    rechtsprechung = Rechtsprechung.from_xml(sample_judgement_xml)
    
    assert rechtsprechung.doknr == "JURE100055033"
    assert rechtsprechung.gertyp == "BGH"
    assert rechtsprechung.spruchkoerper == "9. Zivilsenat"
    assert rechtsprechung.entsch_datum == "20100114"
    assert rechtsprechung.aktenzeichen == "IX ZB 72/08"
    assert rechtsprechung.doktyp == "Beschluss"


def test_rechtsprechung_optional_fields(sample_judgement_xml):
    """Test that optional fields are parsed correctly."""
    rechtsprechung = Rechtsprechung.from_xml(sample_judgement_xml)
    
    assert rechtsprechung.norm is not None
    assert "InsO" in rechtsprechung.norm
    assert rechtsprechung.region is not None
    assert rechtsprechung.region.abk == "DEU"
    assert rechtsprechung.titelzeile is not None
    assert rechtsprechung.tenor is not None
    assert rechtsprechung.gruende is not None


def test_rechtsprechung_content_extraction(sample_judgement_xml):
    """Test that content is properly extracted from XML."""
    rechtsprechung = Rechtsprechung.from_xml(sample_judgement_xml)
    
    # Check that content fields contain text
    assert rechtsprechung.tenor.content is not None
    assert len(rechtsprechung.tenor.content) > 0
    
    if rechtsprechung.gruende:
        assert rechtsprechung.gruende.content is not None
        assert len(rechtsprechung.gruende.content) > 0


def test_rechtsprechung_metadata(sample_judgement_xml):
    """Test that metadata fields are parsed correctly."""
    rechtsprechung = Rechtsprechung.from_xml(sample_judgement_xml)
    
    assert rechtsprechung.identifier is not None
    assert "rechtsprechung-im-internet.de" in rechtsprechung.identifier
    assert rechtsprechung.language == "deutsch"
    assert rechtsprechung.publisher == "BMJV"
    assert rechtsprechung.access_rights == "public"


def _rechtsprechung_with_norm(norm):
    return Rechtsprechung(
        doknr="X", gertyp="BGH", spruchkoerper="1", entsch_datum="20240101",
        aktenzeichen="I ZR 1/24", doktyp="Urteil", norm=norm,
    )


@pytest.mark.parametrize("norm", [None, "", "   "])
def test_get_structured_norms_without_norm(norm):
    """Test that a judgement without norms yields an empty list instead of crashing."""
    assert _rechtsprechung_with_norm(norm).get_structured_norms() == []


def test_get_structured_norms_splits_and_parses():
    """Test that the norm string is split on commas and each part is parsed."""
    norms = _rechtsprechung_with_norm("§ 433 BGB, Art 1 Abs 1 GG").get_structured_norms()

    assert [(n.typ, n.einheit, n.qualifiers, n.gesetz) for n in norms] == [
        ("§", "433", {}, "BGB"),
        ("Art", "1", {"Abs": "1"}, "GG"),
    ]


def test_get_structured_norms_skips_empty_parts():
    """Test that empty parts from stray or trailing commas are ignored."""
    norms = _rechtsprechung_with_norm("§ 433 BGB, , § 212 StGB,").get_structured_norms()

    assert [n.raw.strip() for n in norms] == ["§ 433 BGB", "§ 212 StGB"]
