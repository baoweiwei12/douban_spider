import time
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import Any, List
from pydantic import BaseModel, Field
from typing import Optional, Literal
from retry import retry
from db.schemas import SubjectAwardCreate
import utils


class SubjectAward(SubjectAwardCreate):
    pass


class DoubanSubjectAwardScraper:

    def __init__(
        self,
        douban_subject_id: str,
        proxy_url: str | None = None,
        type: Literal["movie"] = "movie",
    ):
        self.douban_subject_id = douban_subject_id
        self.type = type
        self.subject_url = f"https://{type}.douban.com/subject/{douban_subject_id}/"
        self.awards_url = f"{self.subject_url}awards/"
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

    @retry(tries=3, delay=2, backoff=2, max_delay=10, jitter=(1, 3))
    def _get_html(self):
        response = requests.get(
            self.awards_url, headers=self.headers, proxies=self.proxies
        )
        response.raise_for_status()
        html = response.text
        return html

    def get_data(self):

        data: List[SubjectAward] = []
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.select_one("#content > h1")
        title = title_tag.text.replace("获奖情况", "").strip() if title_tag else None
        awards_divs = soup.select("div.awards")
        award_url = self.awards_url
        for awards_div in awards_divs:
            year_tag = awards_div.select_one(".hd > h2 > .year")
            year = utils.extract_numbers(year_tag.text)[0] if year_tag else None

            award_name_tag = awards_div.select_one(".hd > h2 > a")
            award_name = award_name_tag.text.strip() if award_name_tag else None
            award_name_url = (
                award_name_tag.attrs.get("href") if award_name_tag else None
            )

            award_uls = awards_div.select(".award")
            for award_ul in award_uls:
                specific_award_tag = award_ul.select_one("li:nth-of-type(1)")
                specific_award = specific_award_tag.text if specific_award_tag else None
                award_info = SubjectAward(
                    title=title,
                    award_url=award_url,
                    year=year,
                    award_name=award_name,
                    award_name_url=award_name_url,
                    specific_award=specific_award,
                )
                winner_tags = award_ul.select("a")
                award_info.winner = "/".join(
                    [winner_tag.text for winner_tag in winner_tags]
                )
                award_info.winner_url = "\n".join(
                    [winner_tag.attrs.get("href", "") for winner_tag in winner_tags]
                )
                data.append(award_info)
        return data


if __name__ == "__main__":

    scraper = DoubanSubjectAwardScraper("1301168")
    result = scraper.get_data()
    for i in result:
        print(i.model_dump())
