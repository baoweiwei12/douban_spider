import time
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import Any, List
from pydantic import BaseModel, Field
from typing import Optional, Literal
from retry import retry
from db.schemas import CastCreate
import utils


class Cast(CastCreate):
    pass


class DoubanCastScraper:

    def __init__(
        self,
        douban_subject_id: str,
        proxy_url: str | None = None,
        type: Literal["movie"] = "movie",
    ):
        self.douban_subject_id = douban_subject_id
        self.type = type
        self.subject_url = f"https://{type}.douban.com/subject/{douban_subject_id}/"
        self.cast_url = f"{self.subject_url}celebrities"
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
            self.cast_url, headers=self.headers, proxies=self.proxies
        )
        response.raise_for_status()
        html = response.text
        return html

    def get_data(self):

        data: List[Cast] = []
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        douban_subject_id = self.douban_subject_id
        title_tag = soup.select_one("#content > h1")
        title = (
            title_tag.text.replace("的全部演职员", "").strip() if title_tag else None
        )
        list_wrapper_divs = soup.select(".list-wrapper")
        cast_list_url = self.cast_url
        count = 0
        for list_wrapper_div in list_wrapper_divs:
            role_category_tag = list_wrapper_div.select_one("h2")
            role_category = (
                role_category_tag.text.strip() if role_category_tag else None
            )
            celebrity_lis = list_wrapper_div.select(".celebrity")
            for celebrity_li in celebrity_lis:
                celebrity_a = celebrity_li.select_one(".name > a")
                cast_url = celebrity_a.attrs.get("href") if celebrity_a else None
                cast_name = celebrity_a.text.strip() if celebrity_a else None
                order = count
                count += 1
                specific_role_tag = celebrity_li.select_one(".role")
                specific_role = (
                    specific_role_tag.text.strip() if specific_role_tag else None
                )
                works_span = celebrity_li.select_one(".works")
                works_tags = works_span.select("a") if works_span else None
                representative_work = (
                    "/".join([a.text for a in works_tags]) if works_tags else None
                )
                representative_work_url = (
                    "\n".join([a.attrs.get("href", "") for a in works_tags])
                    if works_tags
                    else None
                )
                data.append(
                    Cast(
                        douban_subject_id=douban_subject_id,
                        title=title,
                        cast_list_url=cast_list_url,
                        role_category=role_category,
                        cast_name=cast_name,
                        cast_url=cast_url,
                        order=str(order),
                        specific_role=specific_role,
                        representative_work=representative_work,
                        representative_work_url=representative_work_url,
                    )
                )
        return data


if __name__ == "__main__":

    scraper = DoubanCastScraper("1301168")
    result = scraper.get_data()
    for i in result:
        print(i.model_dump())
