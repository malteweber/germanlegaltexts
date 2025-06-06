import pytest
from pathlib import Path

@pytest.fixture
def xml_path_infektionsschutzgesetz():
    """Return the path to the Infektionsschutzgesetz XML file."""
    return Path(__file__).parent.parent / "data" / "BJNR104510000.xml"

@pytest.fixture
def xml_content_infektionsschutzgesetz(xml_path_infektionsschutzgesetz):
    """Return the content of the Infektionsschutzgesetz XML file."""
    with open(xml_path_infektionsschutzgesetz, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def all_xml_paths():
    """Return paths to all XML files in the data directory."""
    data_dir = Path(__file__).parent.parent / "data"
    return list(data_dir.glob("*.xml"))

@pytest.fixture
def all_xml_contents(all_xml_paths):
    """Return contents of all XML files in the data directory."""
    result = {}
    for path in all_xml_paths:
        with open(path, 'r', encoding='utf-8') as f:
            result[path.name] = f.read()
    return result