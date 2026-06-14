import asyncio
import io
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
import logging

from .model.Rechtsprechung import Rechtsprechung, RIIIndexItem

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GermanJudgementDownloader:
    """Downloader for German court judgements from rechtsprechung-im-internet.de"""

    base_url = 'https://www.rechtsprechung-im-internet.de'

    def download_judgement_xml(self, url: str) -> str:
        """
        Downloads the XML content of a judgement from a given URL.

        Args:
            url: The URL to the ZIP file containing the judgement XML

        Returns:
            The XML content as a string

        Raises:
            ValueError: If the download fails or the ZIP doesn't contain exactly one XML file
        """
        logger.debug(f"Downloading judgement XML from {url}")
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                response = httpx.get(url, follow_redirects=True)
                if response.status_code != 200:
                    logger.error(f"Download failed: HTTP {response.status_code} for {url}")
                    raise ValueError(f"Failed to download the file: {url} - HTTP {response.status_code}")

                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(tmpdir)

                xml_files = [*Path(tmpdir).glob('*.xml')]
                if len(xml_files) != 1:
                    logger.error(f"Expected 1 XML file, found {len(xml_files)} in {url}")
                    raise RuntimeError(f"Expected 1 XML file, found {len(xml_files)}")
                else:
                    with open(Path(tmpdir) / xml_files[0], 'rb') as xml_file:
                        logger.debug(f"Successfully extracted XML: {xml_files[0].name}")
                        return xml_file.read().decode('utf-8')
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                raise ValueError(f"An error occurred while processing {url}: {str(e)}")

    def download_judgement(self, url: str) -> Rechtsprechung:
        """
        Downloads a judgement and returns it as a Rechtsprechung object.

        Args:
            url: The URL to the ZIP file containing the judgement XML

        Returns:
            A Rechtsprechung object representing the downloaded judgement

        Raises:
            ValueError: If the download fails or the XML cannot be parsed
        """
        xml_content = self.download_judgement_xml(url)
        return Rechtsprechung.from_xml(xml_content)

    def get_all_judgement_index_items(self) -> list[RIIIndexItem]:
        """
        Collects all judgement index items from the rii-toc.xml file.
        This XML file contains metadata for all available judgements.

        Returns:
            A list of RIIIndexItem objects containing metadata for all judgements

        Raises:
            ValueError: If the TOC XML file cannot be downloaded or parsed
        """
        toc_url = f"{self.base_url}/rii-toc.xml"
        logger.debug(f"Fetching judgement index from {toc_url}")

        try:
            response = httpx.get(toc_url, follow_redirects=True)
            if response.status_code != 200:
                logger.error(f"Failed to download TOC: HTTP {response.status_code}")
                raise ValueError(f"Failed to download the TOC XML file: {toc_url} - HTTP {response.status_code}")

            xml_content = response.text
            root = ET.fromstring(xml_content)

            index_items = []

            for item in root.findall('.//item'):
                gericht = item.findtext('gericht')
                entsch_datum = item.findtext('entsch-datum')
                aktenzeichen = item.findtext('aktenzeichen')
                link_element = item.find('link')
                modified = item.findtext('modified')

                if gericht and entsch_datum and aktenzeichen and link_element is not None and link_element.text:
                    link = link_element.text.strip().replace('http://', 'https://', 1)
                    index_items.append(RIIIndexItem(
                        gericht=gericht,
                        entsch_datum=entsch_datum,
                        aktenzeichen=aktenzeichen,
                        link=link,
                        modified=modified or ""
                    ))

            logger.info(f"Retrieved {len(index_items)} judgement entries from index")
            return index_items

        except ET.ParseError as e:
            logger.error(f"Failed to parse TOC XML: {str(e)}")
            raise ValueError(f"Failed to parse the TOC XML file: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing TOC: {str(e)}")
            raise ValueError(f"An error occurred while processing {toc_url}: {str(e)}")

    def download_all_judgements(self) -> list[Rechtsprechung]:
        """
        Downloads all available judgements from rechtsprechung-im-internet.de.

        WARNING: This will download a very large number of judgements and may take
        a significant amount of time and bandwidth.

        Returns:
            A list of Rechtsprechung objects for all available judgements

        Raises:
            ValueError: If any download fails
        """
        index_items = self.get_all_judgement_index_items()
        logger.info(f"Starting download of {len(index_items)} judgements")
        judgements = []

        for i, item in enumerate(index_items, 1):
            try:
                judgement = self.download_judgement(item.link)
                judgements.append(judgement)

                if i % 100 == 0:
                    logger.info(f"Progress: {i}/{len(index_items)} judgements downloaded")

            except Exception as e:
                logger.warning(f"Failed to download judgement {item.aktenzeichen}: {str(e)}")
                continue

        logger.info(f"Completed: {len(judgements)}/{len(index_items)} judgements downloaded successfully")
        return judgements

    def download_first_n_judgements(self, n: int) -> list[Rechtsprechung]:
        """
        Downloads the first n judgements from the index.

        Args:
            n: The number of judgements to download

        Returns:
            A list of up to n Rechtsprechung objects

        Raises:
            ValueError: If n is less than 1 or if the index cannot be retrieved
        """
        if n < 1:
            raise ValueError("n must be at least 1")

        index_items = self.get_all_judgement_index_items()
        items_to_download = index_items[:n]
        logger.info(f"Starting download of first {len(items_to_download)} judgements")

        judgements = []

        for i, item in enumerate(items_to_download, 1):
            try:
                judgement = self.download_judgement(item.link)
                judgements.append(judgement)
                logger.info(f"Progress: {i}/{len(items_to_download)} judgements downloaded")

            except Exception as e:
                logger.warning(f"Failed to download judgement {item.aktenzeichen}: {str(e)}")
                continue

        logger.info(f"Completed: {len(judgements)}/{len(items_to_download)} judgements downloaded successfully")
        return judgements

    def get_judgement_count(self) -> int:
        """
        Returns the total number of available judgements in the index.

        Returns:
            The number of judgements in the rii-toc.xml index

        Raises:
            ValueError: If the index cannot be retrieved
        """
        count = len(self.get_all_judgement_index_items())
        logger.debug(f"Judgement count: {count}")
        return count

    async def _get_all_judgement_index_items_async(self, client: httpx.AsyncClient) -> list[RIIIndexItem]:
        toc_url = f"{self.base_url}/rii-toc.xml"
        logger.debug(f"Fetching judgement index async from {toc_url}")
        try:
            response = await client.get(toc_url)
            if response.status_code != 200:
                logger.error(f"Failed to download TOC: HTTP {response.status_code}")
                raise ValueError(f"Failed to download the TOC XML file: {toc_url} - HTTP {response.status_code}")
            root = ET.fromstring(response.text)
            index_items = []
            for item in root.findall('.//item'):
                gericht = item.findtext('gericht')
                entsch_datum = item.findtext('entsch-datum')
                aktenzeichen = item.findtext('aktenzeichen')
                link_element = item.find('link')
                modified = item.findtext('modified')
                if gericht and entsch_datum and aktenzeichen and link_element is not None and link_element.text:
                    index_items.append(RIIIndexItem(
                        gericht=gericht,
                        entsch_datum=entsch_datum,
                        aktenzeichen=aktenzeichen,
                        link=link_element.text.strip().replace('http://', 'https://', 1),
                        modified=modified or ""
                    ))
            logger.info(f"Retrieved {len(index_items)} judgement entries from index")
            return index_items
        except ET.ParseError as e:
            logger.error(f"Failed to parse TOC XML: {str(e)}")
            raise ValueError(f"Failed to parse the TOC XML file: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing TOC: {str(e)}")
            raise ValueError(f"An error occurred while processing {toc_url}: {str(e)}")

    async def _download_judgement_xml_async(self, client: httpx.AsyncClient, url: str) -> str:
        logger.debug(f"Downloading judgement XML async from {url}")
        try:
            response = await client.get(url)
            if response.status_code != 200:
                logger.error(f"Download failed: HTTP {response.status_code} for {url}")
                raise ValueError(f"Failed to download the file: {url} - HTTP {response.status_code}")
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                xml_files = [f for f in z.namelist() if f.endswith('.xml')]
                if len(xml_files) != 1:
                    logger.error(f"Expected 1 XML file, found {len(xml_files)} in {url}")
                    raise RuntimeError(f"Expected 1 XML file, found {len(xml_files)}")
                return z.read(xml_files[0]).decode('utf-8')
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            raise ValueError(f"An error occurred while processing {url}: {str(e)}")

    async def _download_judgement_async(self, client: httpx.AsyncClient, url: str) -> Rechtsprechung:
        xml_content = await self._download_judgement_xml_async(client, url)
        return Rechtsprechung.from_xml(xml_content)

    async def iter_all_judgements(self, max_per_second: float | None = 1.0) -> AsyncGenerator[Rechtsprechung, None]:
        """
        Asynchronously downloads all judgements and yields them as they complete.

        Downloads are started at a controlled rate and run in parallel — multiple
        downloads can be in-flight simultaneously while new ones are started at
        most max_per_second times per second.

        Args:
            max_per_second: Maximum number of new downloads to start per second.
                            Set to None to start all downloads immediately with no throttle.

        Yields:
            Rechtsprechung objects in completion order (not index order).
        """
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)) as client:
            items = await self._get_all_judgement_index_items_async(client)
            async for judgement in self._iter_judgements(client, items, max_per_second):
                yield judgement

    def iter_first_n_judgements(self, n: int, max_per_second: float | None = 1.0) -> AsyncGenerator[Rechtsprechung, None]:
        """
        Asynchronously downloads the first n judgements and yields them as they complete.

        Downloads are started at a controlled rate and run in parallel — multiple
        downloads can be in-flight simultaneously while new ones are started at
        most max_per_second times per second.

        Args:
            n: The number of judgements to download (must be >= 1).
            max_per_second: Maximum number of new downloads to start per second.
                            Set to None to start all downloads immediately with no throttle.

        Yields:
            Rechtsprechung objects in completion order (not index order).

        Raises:
            ValueError: If n is less than 1.
        """
        if n < 1:
            raise ValueError("n must be at least 1")
        return self._iter_first_n_judgements(n, max_per_second)

    async def _iter_first_n_judgements(self, n: int, max_per_second: float | None) -> AsyncGenerator[Rechtsprechung, None]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)) as client:
            items = await self._get_all_judgement_index_items_async(client)
            async for judgement in self._iter_judgements(client, items[:n], max_per_second):
                yield judgement

    async def _iter_judgements(self, client: httpx.AsyncClient, items: list[RIIIndexItem], max_per_second: float | None) -> AsyncGenerator[Rechtsprechung, None]:
        total = len(items)
        logger.info(f"Starting async download of {total} judgements")
        queue: asyncio.Queue[Rechtsprechung | None] = asyncio.Queue()

        async def _worker(item: RIIIndexItem) -> None:
            try:
                result = await self._download_judgement_async(client, item.link)
                await queue.put(result)
            except Exception as e:
                logger.warning(f"Failed to download judgement {item.aktenzeichen}: {str(e)}")
                await queue.put(None)

        async def _producer() -> None:
            delay = 1.0 / max_per_second if max_per_second is not None else 0.0
            for item in items:
                asyncio.create_task(_worker(item))
                if delay > 0:
                    await asyncio.sleep(delay)

        asyncio.create_task(_producer())

        received = 0
        while received < total:
            result = await queue.get()
            received += 1
            if result is not None:
                yield result

        logger.info(f"Async download of {total} judgements complete")
