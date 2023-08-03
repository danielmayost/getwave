from typing import Callable, List, NamedTuple
from lxml import html
import requests
import asyncio
import aiohttp
import aiofiles
import re

ProgressCallback = Callable[[int, int], None]
HtmlNode = NamedTuple("HtmlNode", [("href", str), ("inner_text", str)])

def parse_string(s: str) -> int | List[int] | str:
    if s.isdigit():
        return int(s)

    segments = s.split(',')
    result: List[int] = []
    for segment in segments:
        segment = segment.strip()

        if '-' in segment:
            start, end = segment.split('-')
            if start.isdigit() and end.isdigit():
                result.extend(range(int(start), int(end) + 1))
            else:
                return s
        elif segment.isdigit():
            result.append(int(segment))
        else:
            return s

    return result

def get_site_page(url: str, progress: ProgressCallback | None = None, expected: int=0) -> bytes:
    response = requests.get(url, stream=progress is not None)
    if response.status_code != 200:
        print("Failed to fetch the page. Status code:", response.status_code)
        exit(1)

    if progress is None:
        return response.content

    total_size = int(response.headers.get('content-length', 0))
    total_size = expected if total_size == 0 else total_size
    block_size = 4096
    content = b""

    for chunk in response.iter_content(block_size):
        content += chunk
        progress(len(content), total_size)

    progress(len(content), len(content))

    return content

def extract_node(html_content: bytes, xpath: str) -> List[HtmlNode]:
    tree = html.fromstring(html_content) # type: ignore
    nodes = tree.xpath(xpath)
    return [HtmlNode(n.get("href"), n.text.strip()) for n in nodes] # type: ignore

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

def fetch_pages_async(urls: List[str], limit_connections: int, progress: ProgressCallback | None = None) -> List[bytes]:
    # This is because the standard ProgressCallback doesn't aggregate the completed notifications.
    class ProgressTracker:
        def __init__(self, total: int, callback: ProgressCallback | None = None):
            self.completed = 0
            self.total = total
            self.lock = asyncio.Lock()
            self.callback = callback

        async def increment(self):
            async with self.lock:
                self.completed += 1
                if self.callback:
                    self.callback(self.completed, self.total)

    # Define fetch one url asynchronously.
    async def fetch_async(url: str, session: aiohttp.ClientSession, progress_tracker: ProgressTracker) -> bytes:
        async with session.get(url) as response:
            content = await response.read()
            await progress_tracker.increment()
            return content

    # Define fetch multiple urls asynchronously.
    async def fetch_all_async(urls: List[str], limit_connections: int, progress: ProgressCallback | None = None) -> List[bytes]:
        connector = aiohttp.TCPConnector(limit=limit_connections)
        progress_tracker = ProgressTracker(len(urls), progress)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [fetch_async(url, session, progress_tracker) for url in urls]
            return await asyncio.gather(*tasks)

    # Fetch all URLs asynchronously and wait for completion.
    return asyncio.run(fetch_all_async(urls, limit_connections, progress))

async def download_async(url: str, dest:str, session: aiohttp.ClientSession, progress: ProgressCallback | None = None) -> None:
    async with session.get(url) as response:
        total_size = int(response.headers.get('content-length', 0))

        async with aiofiles.open(dest, 'wb') as f:
            bytes_downloaded = 0
            while True:
                chunk = await response.content.read(1024 * 8)
                if not chunk:
                    break
                await f.write(chunk)
                bytes_downloaded += len(chunk)
                if progress:
                    progress(bytes_downloaded, total_size)