import time
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List
from pydantic import BaseModel, Field
from typing import Optional, Literal
import re
from retry import retry
from db.schemas import DoubanWorkCreate


class DoubanWork(DoubanWorkCreate):
    pass


class DoubanWorkScraper:

    def __init__(
        self,
        douban_person_id: str,
        cookies: dict[str, str],
        proxy_url: str | None = None,
    ):
        self.douban_person_id = douban_person_id
        self.douban_url = f"https://www.douban.com/personage/{douban_person_id}/"
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "priority": "u=0, i",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        }
        self.proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        self.cookies = cookies

    class LoginRequiredError(Exception):
        pass

    @retry(tries=3, delay=2, backoff=2)
    def _get_douban_works_html(
        self, start_page: int, type: Literal["filmmaker", "writer", "musician"]
    ):
        params = {
            "type": type,
            "start": f"{0 + start_page * 10}",
            "sortby": "collection",
            "role": "",
            "format": "pic",
        }

        response = requests.get(
            self.douban_url + "creations",
            params=params,
            headers=self.headers,
            proxies=self.proxies,
            cookies=self.cookies,
        )
        response.raise_for_status()  # Raise an error for bad responses
        # 检查网页标题
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else ""
        if "登录" in str(title):  # 如果标题中包含“登录”
            raise self.LoginRequiredError("登录限制")
        return soup

    def _extract_filmmaker_works(self, creation: Tag):
        work = DoubanWork(**{"douban_person_id": self.douban_person_id})
        work.douban_url = self.douban_url
        work.star_work_url = self.douban_url + "creations?sortby=time&type=filmmaker"
        work.work_type = "影视"
        work_title_element = creation.select_one("h6 a")
        work.work_name = (
            work_title_element.text if work_title_element is not None else None
        )
        work.work_url = (
            work_title_element.attrs.get("href")
            if work_title_element is not None
            else None
        )
        work.year = (
            element.text.strip("()")
            if (element := creation.select_one("h6 span:nth-of-type(1)")) is not None
            else None
        )
        # 未上映的才有三个span
        if (element := creation.select_one("h6 span:nth-of-type(3)")) is not None:
            work.status = "未上映"
            # 第三个span是role
            work.role = (
                match.group(1).strip()
                if (match := re.search(r"\[([^]]+)\]", element.text)) is not None
                else None
            )
        else:
            work.status = "已上映"
            # 第二个span是role
            role_str = (
                element2.text.strip("()")
                if (element2 := creation.select_one("h6 span:nth-of-type(2)"))
                is not None
                else ""
            )
            work.role = (
                match.group(1).strip()
                if (match := re.search(r"\[([^]]+)\]", role_str)) is not None
                else None
            )
        work.director = (
            element.text.replace("导演：", "").strip()
            if (element := creation.select_one(".roles div:nth-of-type(1)")) is not None
            else None
        )
        work.actors = (
            element.text.replace("主演：", "").strip()
            if (element := creation.select_one(".roles div:nth-of-type(2)")) is not None
            else None
        )
        rate_element = creation.select_one(".rating span:nth-of-type(2)")
        if rate_element is not None:
            work.rating, work.rating_count = (
                rate_element.text.replace(" ", "").replace("人评价", "").split("/")
            )
        return work

    def get_all_filmmaker_list(self, seconds: int = 2) -> List[DoubanWork]:
        soup = self._get_douban_works_html(start_page=0, type="filmmaker")
        results = []
        # 总页数
        total_page_element = soup.select_one(".thispage")
        total_page = int(total_page_element.attrs.get("data-total-page")) if total_page_element else "1"  # type: ignore
        # 剩下的页数
        page_list = [i for i in range(1, int(total_page))]
        # 先搞定一页
        creations = soup.select("ul.creations li.creation")
        for creation in creations:
            work = self._extract_filmmaker_works(creation)
            results.append(work)
        # 剩余页码
        if len(page_list) == 0:
            return results
        for page in page_list:
            soup = self._get_douban_works_html(start_page=page, type="filmmaker")
            creations = soup.select("ul.creations li.creation")
            for creation in creations:
                work = self._extract_filmmaker_works(creation)
                results.append(work)
            time.sleep(seconds)
        return results

    def _extract_writer_works(self, creation: Tag):
        work = DoubanWork(**{"douban_person_id": self.douban_person_id})
        work.douban_url = self.douban_url
        work.star_work_url = self.douban_url + "creations?sortby=time&type=writer"
        work.work_type = "图书"
        work_title_element = creation.select_one("h6 a")
        work.work_name = (
            work_title_element.text if work_title_element is not None else None
        )
        work.work_url = (
            work_title_element.attrs.get("href")
            if work_title_element is not None
            else None
        )
        work.year = (
            element.text.strip("()")
            if (element := creation.select_one("h6 span:nth-of-type(1)")) is not None
            else None
        )
        work.author = (
            element.text.replace("作者：", "").strip()
            if (element := creation.select_one(".roles div:nth-of-type(1)")) is not None
            else None
        )
        work.publisher = (
            element.text.replace("出版社：", "").strip()
            if (element := creation.select_one(".roles div:nth-of-type(2)")) is not None
            else None
        )
        rate_element = creation.select_one(".rating span:nth-of-type(2)")
        if rate_element is not None:
            work.rating, work.rating_count = (
                rate_element.text.replace(" ", "").replace("人评价", "").split("/")
            )
        return work

    def get_all_writer_list(self, seconds: int = 2) -> List[DoubanWork]:
        soup = self._get_douban_works_html(start_page=0, type="writer")
        results = []
        # 总页数
        total_page_element = soup.select_one(".thispage")
        total_page = int(total_page_element.attrs.get("data-total-page")) if total_page_element else "1"  # type: ignore
        # 剩下的页数
        page_list = [i for i in range(1, int(total_page))]
        # 先搞定一页
        creations = soup.select("ul.creations li.creation")
        for creation in creations:
            work = self._extract_writer_works(creation)
            results.append(work)
        # 剩余页码
        if len(page_list) == 0:
            return results
        for page in page_list:
            soup = self._get_douban_works_html(start_page=page, type="writer")
            creations = soup.select("ul.creations li.creation")
            for creation in creations:
                work = self._extract_writer_works(creation)
                results.append(work)
            time.sleep(seconds)
        return results

    def _extract_musician_works(self, creation: Tag):
        work = DoubanWork(**{"douban_person_id": self.douban_person_id})
        work.douban_url = self.douban_url
        work.star_work_url = self.douban_url + "creations?sortby=time&type=musician"
        work.work_type = "音乐"
        work_title_element = creation.select_one("h6 a")
        work.work_name = (
            work_title_element.text if work_title_element is not None else None
        )
        work.work_url = (
            work_title_element.attrs.get("href")
            if work_title_element is not None
            else None
        )
        work.year = (
            element.text.strip("()")
            if (element := creation.select_one("h6 span:nth-of-type(1)")) is not None
            else None
        )
        work.performer = (
            element.text.replace("表演者：", "").strip()
            if (element := creation.select_one(".roles div:nth-of-type(1)")) is not None
            else None
        )
        rate_element = creation.select_one(".rating span:nth-of-type(2)")
        if rate_element is not None:
            work.rating, work.rating_count = (
                rate_element.text.replace(" ", "").replace("人评价", "").split("/")
            )
        return work

    def get_all_musician_list(self, seconds: int = 2) -> List[DoubanWork]:
        soup = self._get_douban_works_html(start_page=0, type="musician")
        results = []
        # 总页数
        total_page_element = soup.select_one(".thispage")
        total_page = int(total_page_element.attrs.get("data-total-page")) if total_page_element else "1"  # type: ignore
        # 剩下的页数
        page_list = [i for i in range(1, int(total_page))]
        # 先搞定一页
        creations = soup.select("ul.creations li.creation")
        for creation in creations:
            work = self._extract_musician_works(creation)
            results.append(work)
        # 剩余页码
        if len(page_list) == 0:
            return results
        for page in page_list:
            soup = self._get_douban_works_html(start_page=page, type="musician")
            creations = soup.select("ul.creations li.creation")
            for creation in creations:
                work = self._extract_musician_works(creation)
                results.append(work)
            time.sleep(seconds)
        return results


if __name__ == "__main__":
    douban_url = "27246769"
    cookies = {
        "bid": "fDuTHxNvuQ0",
        "_pk_id.100001.8cb4": "afbb7e6b550a8132.1736252675.",
        "ct": "y",
        "_ga": "GA1.2.1919025541.1736423961",
        "_ga_Y4GN1R87RG": "GS1.1.1736423960.1.0.1736424001.0.0.0",
        "push_noty_num": "0",
        "push_doumail_num": "0",
        "__utmv": "30149280.28592",
        "__utmc": "30149280",
        "ll": '"118309"',
        "frodotk_db": '"dead754e37b0d1529c085feaa71273f6"',
        "_vwo_uuid_v2": "DCF662625863957C5415FC38359EF9C2F|5d8119a761eb859375e676955136be88",
        "_pk_ref.100001.8cb4": "%5B%22%22%2C%22%22%2C1736821817%2C%22https%3A%2F%2Fwww.bing.com%2F%22%5D",
        "_pk_ses.100001.8cb4": "1",
        "ap_v": "0,6.0",
        "__yadk_uid": "Y9DFTTEx0fDqTItTjeeYrskfJc3498Sz",
        "dbcl2": '"285924458:uJ7VNKW0oJw"',
        "ck": "stRx",
        "__utma": "30149280.447877039.1736353803.1736814350.1736823226.10",
        "__utmz": "30149280.1736823226.10.3.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/",
        "__utmt": "1",
        "__utmb": "30149280.16.10.1736823226",
    }
    scraper = DoubanWorkScraper(douban_url, cookies, "http://127.0.0.1:7890")

    works = scraper.get_all_musician_list()
    for work in works:
        print(work.model_dump_json())
    print(len(works))
    works = scraper.get_all_writer_list()
    for work in works:
        print(work.model_dump_json())
    print(len(works))
    works = scraper.get_all_filmmaker_list()
    for work in works:
        print(work.model_dump_json())
    print(len(works))
