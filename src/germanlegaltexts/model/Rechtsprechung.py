from dataclasses import dataclass, field


@dataclass
class RIIIndexItem:
    """Represents an item from the rii-toc.xml index."""
    gericht: str
    entsch_datum: str
    aktenzeichen: str
    link: str
    modified: str


@dataclass
class Region:
    """Represents the regional information of a judgement."""
    abk: str | None = None
    long: str | None = None


@dataclass
class Content:
    """Represents the content of a section in the judgement."""
    text: str


@dataclass
class Titelzeile:
    """Represents the title line of the judgement."""
    content: str | None = None


@dataclass
class Leitsatz:
    """Represents the headnote (Leitsatz) of the judgement."""
    content: str | None = None


@dataclass
class Tenor:
    """Represents the operative part (Tenor) of the judgement."""
    content: str | None = None


@dataclass
class Tatbestand:
    """Represents the facts (Tatbestand) of the case."""
    content: str | None = None


@dataclass
class Entscheidungsgruende:
    """Represents the reasoning for the decision."""
    content: str | None = None


@dataclass
class Gruende:
    """Represents the grounds/reasoning (Gründe) of the judgement."""
    content: str | None = None


@dataclass
class Abweichende_Meinung:
    """Represents a dissenting opinion."""
    content: str | None = None


@dataclass
class Rechtsprechung:
    """Represents a German court judgement (Rechtsprechung) document."""
    doknr: str
    gertyp: str
    spruchkoerper: str
    entsch_datum: str
    aktenzeichen: str
    doktyp: str
    ecli: str | None = None
    gerort: str | None = None
    norm: str | None = None
    vorinstanz: str | None = None
    region: Region | None = None
    mitwirkung: str | None = None
    titelzeile: Titelzeile | None = None
    leitsatz: Leitsatz | None = None
    sonstosatz: str | None = None
    tenor: Tenor | None = None
    tatbestand: Tatbestand | None = None
    entscheidungsgruende: Entscheidungsgruende | None = None
    gruende: Gruende | None = None
    abwmeinung: Abweichende_Meinung | None = None
    sonstlt: str | None = None
    identifier: str | None = None
    coverage: str | None = None
    language: str | None = None
    publisher: str | None = None
    access_rights: str | None = None

    @classmethod
    def from_xml(cls, xml_content: str) -> 'Rechtsprechung':
        """
        Parse the XML content and create a Rechtsprechung instance.

        Args:
            xml_content: The XML content as a string

        Returns:
            An instance of Rechtsprechung
        """
        import xml.etree.ElementTree as ET
        from io import StringIO

        tree = ET.parse(StringIO(xml_content))
        root = tree.getroot()

        def get_text_content(element) -> str | None:
            """Extract text content from an element and its children."""
            if element is None:
                return None
            
            texts = []
            for text in element.itertext():
                cleaned = text.strip()
                if cleaned:
                    texts.append(cleaned)
            
            return ' '.join(texts) if texts else None

        region = None
        region_elem = root.find('region')
        if region_elem is not None:
            region = Region(
                abk=region_elem.findtext('abk'),
                long=region_elem.findtext('long')
            )

        titelzeile = None
        titelzeile_elem = root.find('titelzeile')
        if titelzeile_elem is not None:
            titelzeile = Titelzeile(content=get_text_content(titelzeile_elem))

        leitsatz = None
        leitsatz_elem = root.find('leitsatz')
        if leitsatz_elem is not None:
            leitsatz = Leitsatz(content=get_text_content(leitsatz_elem))

        tenor = None
        tenor_elem = root.find('tenor')
        if tenor_elem is not None:
            tenor = Tenor(content=get_text_content(tenor_elem))

        tatbestand = None
        tatbestand_elem = root.find('tatbestand')
        if tatbestand_elem is not None:
            tatbestand = Tatbestand(content=get_text_content(tatbestand_elem))

        entscheidungsgruende = None
        entscheidungsgruende_elem = root.find('entscheidungsgruende')
        if entscheidungsgruende_elem is not None:
            entscheidungsgruende = Entscheidungsgruende(
                content=get_text_content(entscheidungsgruende_elem)
            )

        gruende = None
        gruende_elem = root.find('gruende')
        if gruende_elem is not None:
            gruende = Gruende(content=get_text_content(gruende_elem))

        abwmeinung = None
        abwmeinung_elem = root.find('abwmeinung')
        if abwmeinung_elem is not None:
            abwmeinung = Abweichende_Meinung(content=get_text_content(abwmeinung_elem))

        return cls(
            doknr=root.findtext('doknr') or "",
            ecli=root.findtext('ecli') or None,
            gertyp=root.findtext('gertyp') or "",
            gerort=root.findtext('gerort') or None,
            spruchkoerper=root.findtext('spruchkoerper') or "",
            entsch_datum=root.findtext('entsch-datum') or "",
            aktenzeichen=root.findtext('aktenzeichen') or "",
            doktyp=root.findtext('doktyp') or "",
            norm=root.findtext('norm') or None,
            vorinstanz=root.findtext('vorinstanz') or None,
            region=region,
            mitwirkung=root.findtext('mitwirkung') or None,
            titelzeile=titelzeile,
            leitsatz=leitsatz,
            sonstosatz=root.findtext('sonstosatz') or None,
            tenor=tenor,
            tatbestand=tatbestand,
            entscheidungsgruende=entscheidungsgruende,
            gruende=gruende,
            abwmeinung=abwmeinung,
            sonstlt=root.findtext('sonstlt') or None,
            identifier=root.findtext('identifier') or None,
            coverage=root.findtext('coverage') or None,
            language=root.findtext('language') or None,
            publisher=root.findtext('publisher') or None,
            access_rights=root.findtext('accessRights') or None,
        )
