from dataclasses import dataclass, field

@dataclass
class Fundstelle:
    """Represents a citation/reference in the legal text."""
    typ: str
    periodikum: str | None = None
    zitstelle: str | None = None

@dataclass
class Standangabe:
    """Represents the status information of the legal text."""
    checked: str
    standtyp: str
    standkommentar: str | None = None

@dataclass
class Metadaten:
    """Represents metadata of a norm/section in the legal text."""
    jurabk: str
    amtabk: str | None = None
    ausfertigung_datum: str | None = None
    fundstelle: Fundstelle | None = None
    kurzue: str | None = None
    langue: str | None = None
    standangabe: Standangabe | None = None
    enbez: str | None = None
    titel: str | None = None
    titel_format: str | None = None
    gliederungseinheit: dict[str, str] | None = None

@dataclass
class Content:
    """Represents the content of a text section."""
    text: str

@dataclass
class Fussnoten:
    """Represents footnotes in the legal text."""
    content: Content | None = None

@dataclass
class Text:
    """Represents a text element with format and content."""
    format: str
    content: Content | None = None

@dataclass
class Textdaten:
    """Represents the text data of a norm/section."""
    text: Text | None = None
    fussnoten: Fussnoten | None = None
    content: Content | None = None

@dataclass
class Norm:
    """Represents a norm/section in the legal text."""
    builddate: str
    doknr: str
    metadaten: Metadaten
    textdaten: Textdaten

@dataclass
class Gesetzbuch:
    """Represents a German legal code document."""
    builddate: str
    doknr: str
    norms: list[Norm] = field(default_factory=list)

    @classmethod
    def from_xml(cls, xml_content: str) -> 'Gesetzbuch':
        """
        Parse the XML content and create a Gesetzbuch instance.

        Args:
            xml_content: The XML content as a string

        Returns:
            An instance of Gesetzbuch
        """
        import xml.etree.ElementTree as ET
        from io import StringIO

        tree = ET.parse(StringIO(xml_content))
        root = tree.getroot()

        gesetz = cls(
            builddate=root.get('builddate'),
            doknr=root.get('doknr'),
            norms=[]
        )
        for norm_elem in root.findall('norm'):
            metadaten_elem = norm_elem.find('metadaten')
            if metadaten_elem is None:
                continue

            metadaten = Metadaten(jurabk=metadaten_elem.findtext('jurabk') or "")
            if metadaten_elem.find('amtabk') is not None:
                metadaten.amtabk = metadaten_elem.findtext('amtabk')

            if metadaten_elem.find('ausfertigung-datum') is not None:
                metadaten.ausfertigung_datum = metadaten_elem.findtext('ausfertigung-datum')

            if metadaten_elem.find('kurzue') is not None:
                metadaten.kurzue = metadaten_elem.findtext('kurzue')

            if metadaten_elem.find('langue') is not None:
                metadaten.langue = metadaten_elem.findtext('langue')

            if metadaten_elem.find('enbez') is not None:
                metadaten.enbez = metadaten_elem.findtext('enbez')

            if metadaten_elem.find('titel') is not None:
                metadaten.titel = metadaten_elem.findtext('titel')
                titel_elem = metadaten_elem.find('titel')
                if titel_elem is not None and 'format' in titel_elem.attrib:
                    metadaten.titel_format = titel_elem.get('format')

            fundstelle_elem = metadaten_elem.find('fundstelle')
            if fundstelle_elem is not None:
                fundstelle = Fundstelle(
                    typ=fundstelle_elem.get('typ', ""),
                    periodikum=fundstelle_elem.findtext('periodikum'),
                    zitstelle=fundstelle_elem.findtext('zitstelle')
                )
                metadaten.fundstelle = fundstelle

            standangabe_elem = metadaten_elem.find('standangabe')
            if standangabe_elem is not None:
                standangabe = Standangabe(
                    checked=standangabe_elem.get('checked', ""),
                    standtyp=standangabe_elem.findtext('standtyp') or "",
                    standkommentar=standangabe_elem.findtext('standkommentar')
                )
                metadaten.standangabe = standangabe
            gliederungseinheit_elem = metadaten_elem.find('gliederungseinheit')
            if gliederungseinheit_elem is not None:
                gliederungseinheit = {}
                for child in gliederungseinheit_elem:
                    gliederungseinheit[child.tag] = child.text
                metadaten.gliederungseinheit = gliederungseinheit

            textdaten_elem = norm_elem.find('textdaten')
            textdaten = Textdaten()

            text_elem = textdaten_elem.find('text') if textdaten_elem is not None else None
            if text_elem is not None:
                text = Text(format=text_elem.get('format', ""))
                content_elem = text_elem.find('Content')
                if content_elem is not None:
                    content_text = ET.tostring(content_elem, encoding='unicode', method='text')
                    text.content = Content(text=content_text)
                textdaten.text = text

            fussnoten_elem = textdaten_elem.find('fussnoten') if textdaten_elem is not None else None
            if fussnoten_elem is not None:
                fussnoten = Fussnoten()
                content_elem = fussnoten_elem.find('Content')
                if content_elem is not None:
                    content_text = ET.tostring(content_elem, encoding='unicode', method='text')
                    fussnoten.content = Content(text=content_text)
                textdaten.fussnoten = fussnoten
            norm = Norm(
                builddate=norm_elem.get('builddate', ""),
                doknr=norm_elem.get('doknr', ""),
                metadaten=metadaten,
                textdaten=textdaten
            )
            gesetz.norms.append(norm)

        return gesetz

    def get_paragraph(self, paragraph_number: str) -> Norm | None:
        """
        Get a specific paragraph by its number.

        Args:
            paragraph_number: The paragraph number (e.g., "§ 1")

        Returns:
            The Norm object for the paragraph, or None if not found
        """
        for norm in self.norms:
            if norm.metadaten.enbez == paragraph_number:
                return norm
        return None

    def get_section(self, section_number: str) -> list[Norm]:
        """
        Get all norms in a specific section.

        Args:
            section_number: The section number (e.g., "1. Abschnitt")

        Returns:
            A list of Norm objects in the section
        """
        result = []
        for norm in self.norms:
            if (norm.metadaten.gliederungseinheit and 
                norm.metadaten.gliederungseinheit.get('gliederungsbez') == section_number):
                result.append(norm)
        return result

    def get_all_paragraphs(self) -> list[str]:
        """
        Get a list of all paragraph numbers.

        Returns:
            A list of paragraph numbers
        """
        result = []
        for norm in self.norms:
            if norm.metadaten.enbez and norm.metadaten.enbez.startswith('§'):
                result.append(norm.metadaten.enbez)
        return result

    def get_all_sections(self) -> list[str]:
        """
        Get a list of all section titles.

        Returns:
            A list of section titles
        """
        result = []
        for norm in self.norms:
            if (norm.metadaten.gliederungseinheit and 
                'gliederungstitel' in norm.metadaten.gliederungseinheit):
                result.append(norm.metadaten.gliederungseinheit['gliederungstitel'])
        return result
