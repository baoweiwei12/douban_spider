import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List
from pydantic import BaseModel, Field
from typing import Optional, Literal
from retry import retry
from db.schemas import AwardInfoCreate


class DoubanAwardScraper:
    def __init__(
        self,
        douban_person_id: str,
        proxy_url: str | None = None,
        cookies: dict[str, str] = {},
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
        self.star_award_url = self.douban_url + "awards"
        self.cookies = cookies

    class LoginRequiredError(Exception):
        pass

    @retry(tries=3, delay=2, backoff=2, max_delay=10, jitter=(1, 3))
    def _get_award_html(self):
        response = requests.get(
            self.star_award_url,
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

    def get_awards_list(self):
        results: List[AwardInfoCreate] = []
        soup = self._get_award_html()
        awards_lis = soup.select(".awards-with-year .year-group")
        for award_li in awards_lis:
            year = (
                element.text.strip()
                if (element := award_li.select_one("h2")) is not None
                else None
            )
            awards_infos_li = award_li.select(".awards li")
            for award_info_li in awards_infos_li:
                award_info = AwardInfoCreate(douban_person_id=self.douban_person_id)
                award_info.douban_url = self.douban_url
                award_info.star_award_url = self.star_award_url
                award_info.year = year
                award_info.specific_award = award_info_li.text.strip()
                award_name_element = award_info_li.select_one("a:nth-of-type(1)")
                if award_name_element is not None:
                    award_info.award_name = award_name_element.text.strip()
                    award_info.award_name_url = award_name_element.attrs.get("href")
                award_work_element = award_info_li.select_one("a:nth-of-type(2)")
                if award_work_element is not None:
                    award_info.award_work = award_work_element.text.strip()
                    award_info.work_homepage_url = award_work_element.attrs.get("href")
                results.append(award_info)
        return results


if __name__ == "__main__":
    douban_url = "27246769"
    proxy_url = "http://127.0.0.1:7890"
    scraper = DoubanAwardScraper(douban_url, proxy_url)
    results = scraper.get_awards_list()
    for award_info in scraper.get_awards_list():
        print(award_info.model_dump_json())
