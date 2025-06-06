import pytest
from src.germanlegaltexts.model.Gesetzbuch import Gesetzbuch

class TestGesetzbuch:
    def test_from_xml(self, xml_content_infektionsschutzgesetz):
        """Test parsing XML content into a Gesetzbuch instance."""
        gesetz = Gesetzbuch.from_xml(xml_content_infektionsschutzgesetz)

        assert gesetz.doknr == "BJNR104510000"
        assert gesetz.builddate == "20240822214507"
        assert len(gesetz.norms) > 0

    def test_get_all_paragraphs(self, xml_content_infektionsschutzgesetz):
        """Test retrieving all paragraphs from a Gesetzbuch instance."""
        gesetz = Gesetzbuch.from_xml(xml_content_infektionsschutzgesetz)
        paragraphs = gesetz.get_all_paragraphs()

        assert len(paragraphs) > 0
        assert all(p.startswith('§') for p in paragraphs)
        assert "§ 1" in paragraphs

    def test_get_all_sections(self, xml_content_infektionsschutzgesetz):
        """Test retrieving all sections from a Gesetzbuch instance."""
        gesetz = Gesetzbuch.from_xml(xml_content_infektionsschutzgesetz)
        sections = gesetz.get_all_sections()

        assert len(sections) > 0
        assert "Allgemeine Vorschriften" in sections

    def test_get_paragraph(self, xml_content_infektionsschutzgesetz):
        """Test retrieving a specific paragraph from a Gesetzbuch instance."""
        gesetz = Gesetzbuch.from_xml(xml_content_infektionsschutzgesetz)
        paragraph = gesetz.get_paragraph("§ 1")

        assert paragraph is not None
        assert paragraph.metadaten.enbez == "§ 1"
        assert paragraph.metadaten.titel == "Zweck des Gesetzes"
        assert paragraph.textdaten.text is not None
        assert paragraph.textdaten.text.content is not None
        assert "Zweck des Gesetzes ist es" in paragraph.textdaten.text.content.text

    def test_get_section(self, xml_content_infektionsschutzgesetz):
        """Test retrieving a specific section from a Gesetzbuch instance."""
        gesetz = Gesetzbuch.from_xml(xml_content_infektionsschutzgesetz)
        section = gesetz.get_section("1. Abschnitt")

        assert len(section) > 0
        assert all(norm.metadaten.gliederungseinheit.get('gliederungsbez') == "1. Abschnitt" 
                  for norm in section if norm.metadaten.gliederungseinheit)

    def test_multiple_xml_files(self, all_xml_contents):
        """Test parsing multiple XML files into Gesetzbuch instances."""
        for filename, content in all_xml_contents.items():
            gesetz = Gesetzbuch.from_xml(content)

            assert gesetz.doknr is not None
            assert gesetz.builddate is not None
            assert len(gesetz.norms) > 0

            paragraphs = gesetz.get_all_paragraphs()
            sections = gesetz.get_all_sections()

            assert isinstance(paragraphs, list)
            assert isinstance(sections, list)
