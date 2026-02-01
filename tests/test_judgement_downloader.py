import pytest
from germanlegaltexts.GermanJudgementDownloader import GermanJudgementDownloader
from germanlegaltexts.model.Rechtsprechung import Rechtsprechung, RIIIndexItem


@pytest.fixture
def downloader():
    """Provide a GermanJudgementDownloader instance."""
    return GermanJudgementDownloader()


def test_downloader_creation(downloader):
    """Test that the downloader can be instantiated."""
    assert downloader is not None
    assert downloader.base_url == 'https://www.rechtsprechung-im-internet.de'


def test_get_all_judgement_index_items(downloader):
    """Test fetching all judgement index items."""
    items = downloader.get_all_judgement_index_items()
    
    assert isinstance(items, list)
    assert len(items) > 0
    
    # Check first item structure
    first_item = items[0]
    assert isinstance(first_item, RIIIndexItem)
    assert first_item.gericht is not None
    assert first_item.entsch_datum is not None
    assert first_item.aktenzeichen is not None
    assert first_item.link.startswith('http')
    assert first_item.link.endswith('.zip')


def test_get_judgement_count(downloader):
    """Test getting the total count of judgements."""
    count = downloader.get_judgement_count()
    
    assert isinstance(count, int)
    assert count > 0


def test_download_judgement(downloader):
    """Test downloading a single judgement."""
    # Get first item from index
    items = downloader.get_all_judgement_index_items()
    first_item = items[0]
    
    # Download it
    rechtsprechung = downloader.download_judgement(first_item.link)
    
    assert isinstance(rechtsprechung, Rechtsprechung)
    assert rechtsprechung.doknr is not None
    assert rechtsprechung.gertyp is not None
    assert rechtsprechung.aktenzeichen is not None


def test_download_first_n_judgements(downloader):
    """Test downloading the first n judgements."""
    n = 3
    judgements = downloader.download_first_n_judgements(n)
    
    assert isinstance(judgements, list)
    assert len(judgements) <= n  # May be fewer if some downloads fail
    assert len(judgements) > 0
    
    for judgement in judgements:
        assert isinstance(judgement, Rechtsprechung)


def test_download_first_n_judgements_invalid_n(downloader):
    """Test that invalid n values raise an error."""
    with pytest.raises(ValueError, match="n must be at least 1"):
        downloader.download_first_n_judgements(0)
    
    with pytest.raises(ValueError, match="n must be at least 1"):
        downloader.download_first_n_judgements(-5)


def test_download_judgement_xml(downloader):
    """Test downloading raw XML content."""
    items = downloader.get_all_judgement_index_items()
    first_item = items[0]
    
    xml_content = downloader.download_judgement_xml(first_item.link)
    
    assert isinstance(xml_content, str)
    assert '<?xml' in xml_content
    assert '<dokument>' in xml_content
    assert '</dokument>' in xml_content
