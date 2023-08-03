from typing import List
from station import RadioStation, Broadcast, ProgressCallback
import utils
import re

class KolHayStation(RadioStation):
    def __init__(self) -> None:
        super().__init__("Kol-Hay")
        self._program_list: List[str] = []

    def load_programs(self) -> List[str]:
        html_content = utils.get_site_page("https://www.93fm.co.il/radio/broadcast/")
        nodes = utils.extract_node(html_content, "//select[@class='program-name']/option")

        self._program_list = [program.inner_text for program in nodes[1:]]
        return self._program_list

    def load_broadcasts(self, program: str | int, progress: ProgressCallback | None = None) -> List[Broadcast]:
        if len(self._program_list) < 1:
            self.load_programs()

        broadcasts: List[Broadcast] = []

        # Achive the program page
        program_name = self._get_program_name(program)
        search_url = f"https://www.93fm.co.il/radio/broadcast/?program-name={program_name}"
        html_content = utils.get_site_page(search_url)
        nodes = utils.extract_node(html_content, "//div[@class='list']/ul/li/a")
        if len(nodes) < 1:
            return []
        
        html_content = utils.get_site_page(nodes[0].href)
        nodes = utils.extract_node(html_content, "//p[@id='breadcrumbs']/span/span/a")

        # This is program page
        html_content = utils.get_site_page(nodes[len(nodes) - 1].href)

        #Extract the program name
        match = re.search(r'/program/([^/]+)/', nodes[len(nodes) - 1].href)
        if match:
            program_name = match.group(1)
        else:
            return []
        
        # Extract the and the last page
        last_page = 1
        nodes = utils.extract_node(html_content, "//ul[@class='pagination']/li/a")
        if len(nodes) > 0:
            match = re.search(r'/page/(\d+)/', nodes[len(nodes) - 1].href)
            if match:
                last_page = int(match.group(1))

        # Fetch all program pages
        urls: List[str] = [f"https://www.93fm.co.il/radio/program/{program_name}/page/{i}" for i in range(1, last_page + 1)]
        results = utils.fetch_pages_async(urls, 50)

        # Fetch all broadcasts from program pages
        urls.clear()
        for page in results:
            nodes = utils.extract_node(page, "//section[@class='latest-broadcasts']/ul/li/article/h1/a")
            urls.extend([n.href for n in nodes])
        
        results = utils.fetch_pages_async(urls, 50, progress)

        # Extract the broadcast files from broadcast pages
        # Each page can contain multiple broadcasts, see https://www.93fm.co.il/radio/broadcast/856670/
        for page in results:
            name_nodes = utils.extract_node(page, "//main[@class='main program']/h1")
            file_nodes = utils.extract_node(page, "//div[@class='player-position']/audio/a")
            names = [name_nodes[0].inner_text for _ in file_nodes]
            if len(file_nodes) > 1:
                names = [f"{name} - {i}" for i, name in enumerate(names, 1)]

            broadcasts.extend([Broadcast(name, file_node.href) for name, file_node in zip(names, file_nodes)])

        return broadcasts

    def _get_program_name(self, program: str | int) -> str:
        if isinstance(program, int):
            return self._program_list[program].replace(' ', '+')
        else:
            return program.replace(' ', '+')