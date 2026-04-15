import io
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from germanlegaltexts.GermanJudgementDownloader import GermanJudgementDownloader
from germanlegaltexts.GermanLawDownloader import GermanLawDownloader
from germanlegaltexts.model.Gesetzbuch import Gesetzbuch
from germanlegaltexts.model.Rechtsprechung import Rechtsprechung


# --- Helpers ---

def make_zip(xml_content: str, filename: str = "test.xml") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(filename, xml_content)
    return buf.getvalue()


def make_mock_client(*responses):
    """Return a mock httpx.AsyncClient whose .get() returns responses in order."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=list(responses))
    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_client)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    return mock_context


LAW_TOC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<items>
  <item><title>Gesetz A</title><link>http://example.com/lawa/xml.zip</link></item>
  <item><title>Gesetz B</title><link>http://example.com/lawb/xml.zip</link></item>
</items>"""

LAW_XML = """<?xml version="1.0" encoding="UTF-8"?>
<dokumente builddate="2023-01-01" doknr="TEST001">
  <norm builddate="2023-01-01" doknr="TEST001">
    <metadaten>
      <jurabk>TestGesetz</jurabk>
      <enbez>§ 1</enbez>
      <titel>Geltungsbereich</titel>
    </metadaten>
    <textdaten>
      <text format="XML"><Content>Dieser Text gilt.</Content></text>
    </textdaten>
  </norm>
</dokumente>"""

JUDGEMENT_TOC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<items>
  <item>
    <gericht>BGH</gericht>
    <entsch-datum>2023-01-15</entsch-datum>
    <aktenzeichen>IX ZB 1/23</aktenzeichen>
    <link>http://example.com/j1.zip</link>
    <modified>2023-02-01</modified>
  </item>
  <item>
    <gericht>BVerfG</gericht>
    <entsch-datum>2023-03-10</entsch-datum>
    <aktenzeichen>1 BvR 100/23</aktenzeichen>
    <link>http://example.com/j2.zip</link>
    <modified>2023-03-15</modified>
  </item>
</items>"""

JUDGEMENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<dokument>
  <doknr>JURE230001</doknr>
  <gertyp>BGH</gertyp>
  <gerort>Karlsruhe</gerort>
  <spruchkoerper>IX. Zivilsenat</spruchkoerper>
  <entsch-datum>20230115</entsch-datum>
  <aktenzeichen>IX ZB 1/23</aktenzeichen>
  <doktyp>Beschluss</doktyp>
  <tenor><div><p>Der Antrag wird abgelehnt.</p></div></tenor>
  <gruende><div><p>1. Die Revision ist unbegründet.</p></div></gruende>
</dokument>"""


# --- GermanLawDownloader async tests ---

class TestIterAllLawBooks:
    async def test_yields_gesetzbuch_objects(self):
        toc_response = MagicMock(status_code=200, text=LAW_TOC_XML)
        law_zip = make_zip(LAW_XML)
        law_response = MagicMock(status_code=200, content=law_zip)

        mock_ctx = make_mock_client(toc_response, law_response, law_response)

        downloader = GermanLawDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            results = [book async for book in downloader.iter_all_law_books(max_per_second=None)]

        assert len(results) == 2
        assert all(isinstance(r, Gesetzbuch) for r in results)

    async def test_skips_failed_downloads(self):
        toc_response = MagicMock(status_code=200, text=LAW_TOC_XML)
        law_zip = make_zip(LAW_XML)
        ok_response = MagicMock(status_code=200, content=law_zip)
        fail_response = MagicMock(status_code=404, content=b"")

        mock_ctx = make_mock_client(toc_response, ok_response, fail_response)

        downloader = GermanLawDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            results = [book async for book in downloader.iter_all_law_books(max_per_second=None)]

        assert len(results) == 1
        assert isinstance(results[0], Gesetzbuch)

    async def test_toc_failure_raises(self):
        toc_response = MagicMock(status_code=500, text="")
        mock_ctx = make_mock_client(toc_response)

        downloader = GermanLawDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            with pytest.raises(ValueError):
                async for _ in downloader.iter_all_law_books(max_per_second=None):
                    pass

    async def test_throttle_none_no_sleep(self):
        """With max_per_second=None, asyncio.sleep should never be called."""
        toc_response = MagicMock(status_code=200, text=LAW_TOC_XML)
        law_zip = make_zip(LAW_XML)
        law_response = MagicMock(status_code=200, content=law_zip)
        mock_ctx = make_mock_client(toc_response, law_response, law_response)

        downloader = GermanLawDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                results = [book async for book in downloader.iter_all_law_books(max_per_second=None)]

        mock_sleep.assert_not_called()
        assert len(results) == 2

class TestIterAllJudgements:
    async def test_yields_rechtsprechung_objects(self):
        toc_response = MagicMock(status_code=200, text=JUDGEMENT_TOC_XML)
        j_zip = make_zip(JUDGEMENT_XML)
        j_response = MagicMock(status_code=200, content=j_zip)

        mock_ctx = make_mock_client(toc_response, j_response, j_response)

        downloader = GermanJudgementDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            results = [j async for j in downloader.iter_all_judgements(max_per_second=None)]

        assert len(results) == 2
        assert all(isinstance(r, Rechtsprechung) for r in results)

    async def test_skips_failed_downloads(self):
        toc_response = MagicMock(status_code=200, text=JUDGEMENT_TOC_XML)
        j_zip = make_zip(JUDGEMENT_XML)
        ok_response = MagicMock(status_code=200, content=j_zip)
        fail_response = MagicMock(status_code=500, content=b"")

        mock_ctx = make_mock_client(toc_response, ok_response, fail_response)

        downloader = GermanJudgementDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            results = [j async for j in downloader.iter_all_judgements(max_per_second=None)]

        assert len(results) == 1


class TestIterFirstNJudgements:
    async def test_yields_n_judgements(self):
        toc_response = MagicMock(status_code=200, text=JUDGEMENT_TOC_XML)
        j_zip = make_zip(JUDGEMENT_XML)
        j_response = MagicMock(status_code=200, content=j_zip)

        mock_ctx = make_mock_client(toc_response, j_response)

        downloader = GermanJudgementDownloader()
        with patch('httpx.AsyncClient', return_value=mock_ctx):
            results = [j async for j in downloader.iter_first_n_judgements(1, max_per_second=None)]

        assert len(results) == 1
        assert isinstance(results[0], Rechtsprechung)

    def test_invalid_n_raises_immediately(self):
        downloader = GermanJudgementDownloader()
        with pytest.raises(ValueError, match="n must be at least 1"):
            downloader.iter_first_n_judgements(0)

    def test_negative_n_raises_immediately(self):
        downloader = GermanJudgementDownloader()
        with pytest.raises(ValueError, match="n must be at least 1"):
            downloader.iter_first_n_judgements(-5)
