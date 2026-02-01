import pytest
from pathlib import Path

@pytest.fixture
def xml_path_infektionsschutzgesetz():
    """Return the path to the Infektionsschutzgesetz XML file."""
    path = Path(__file__).parent.parent / "data" / "BJNR104510000.xml"
    if not path.exists():
        pytest.skip(f"Test data file not found: {path}. Run the downloader to fetch test data.")
    return path

@pytest.fixture
def xml_content_infektionsschutzgesetz(xml_path_infektionsschutzgesetz):
    """Return the content of the Infektionsschutzgesetz XML file."""
    with open(xml_path_infektionsschutzgesetz, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def all_xml_paths():
    """Return paths to all XML files in the data directory."""
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        return []
    return list(data_dir.glob("*.xml"))

@pytest.fixture
def all_xml_contents(all_xml_paths):
    """Return contents of all XML files in the data directory."""
    result = {}
    for path in all_xml_paths:
        with open(path, 'r', encoding='utf-8') as f:
            result[path.name] = f.read()
    return result

@pytest.fixture
def sample_judgement_xml():
    """Return a sample judgement XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE dokument
  SYSTEM "https://www.rechtsprechung-im-internet.de/dtd/v1/rii-dok.dtd">
<dokument>
   <doknr>JURE100055033</doknr>
   <ecli/>
   <gertyp>BGH</gertyp>
   <gerort/>
   <spruchkoerper>9. Zivilsenat</spruchkoerper>
   <entsch-datum>20100114</entsch-datum>
   <aktenzeichen>IX ZB 72/08</aktenzeichen>
   <doktyp>Beschluss</doktyp>
   <norm>§ 4 InsO, § 13 ZPO, § 251 ZPO</norm>
   <vorinstanz>vorgehend LG Aachen, 17. März 2008, Az: 6 T 104/07, Beschluss</vorinstanz>
   <region>
      <abk>DEU</abk>
      <long>Bundesrepublik Deutschland</long>
   </region>
   <mitwirkung/>
   <titelzeile>
      <dl class="RspDL">
         <dt/>
         <dd>
            <p>Insolvenzverfahren: Anwendbarkeit der Vorschrift über das Ruhen des Verfahrens</p>
         </dd>
      </dl>
   </titelzeile>
   <leitsatz/>
   <sonstosatz/>
   <tenor>
      <div>
         <dl class="RspDL">
            <dt/>
            <dd>
               <p>Der Antrag wird abgelehnt.</p>
            </dd>
         </dl>
      </div>
   </tenor>
   <tatbestand/>
   <entscheidungsgruende/>
   <gruende>
      <div>
         <dl class="RspDL">
            <dt>
               <a name="rd_1">1</a>
            </dt>
            <dd>
               <p>1. Einer Entscheidung steht nicht entgegen, dass die Schuldnerin das Ruhen des Verfahrens beantragt hat.</p>
            </dd>
         </dl>
      </div>
   </gruende>
   <abwmeinung/>
   <sonstlt/>
   <identifier>http://www.rechtsprechung-im-internet.de/jportal/?quelle=jlink&amp;docid=jb-JURE100055033</identifier>
   <coverage>Deutschland</coverage>
   <language>deutsch</language>
   <publisher>BMJV</publisher>
   <accessRights>public</accessRights>
</dokument>
"""