import time
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import Any, List
from pydantic import BaseModel, Field
from typing import Optional, Literal
from retry import retry
from db.schemas import CollaborationInfoCreate


class CollaborationInfo(CollaborationInfoCreate):
    pass


class DoubanCollaborationScraper:

    def __init__(self, douban_person_id: str, proxy_url: str | None = None):
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
        self.collaboration_url = self.douban_url + "partners"

    @retry(tries=3, delay=2, backoff=2, max_delay=10, jitter=(1, 3))
    def _get_json_data(self, start: int = 0, count=10) -> Any:
        params = {
            "start": f"{start}",
            "count": f"{count}",
            "name": "",
            "simple": "0",
        }
        response = requests.get(
            f"https://m.douban.com/rexxar/api/v2/elessar/subject/{self.douban_url.split('/')[-2]}/partners",
            params=params,
            headers=self.headers,
            proxies=self.proxies,
        )
        response.raise_for_status()  # Raise an error for bad responses
        return response.json().get("items")

    def get_all_collaborations_list(self, seconds: int = 2) -> List[CollaborationInfo]:
        """获取所有合作信息"""
        collaborations = []
        start = 0
        count = 10
        while True:
            items = self._get_json_data(start, count)
            for item in items:
                collaboration = CollaborationInfo(
                    douban_person_id=self.douban_person_id,
                    douban_url=self.douban_url,
                    collaboration_url=self.collaboration_url,
                    collaborator_name=item.get("name"),
                    collaborator_homepage_url=item.get("url"),
                    collaborator_profession=item.get("profession"),
                    collaboration_count=item.get("joint_works_cnt"),
                    collaboration_works=[
                        work.get("name")
                        for work in (
                            item.get("joint_works") if item.get("joint_works") else []
                        )
                    ],
                    collaboration_works_homepage_url=[
                        work.get("url")
                        for work in (
                            item.get("joint_works") if item.get("joint_works") else []
                        )
                    ],
                    collaborator_douban_followers=item.get("fans_cnt"),
                )
                collaborations.append(collaboration)
            if len(items) < count:
                break
            start += count
            time.sleep(seconds)
        return collaborations


if __name__ == "__main__":
    douban_url = "34880873"
    proxy_url = "http://127.0.0.1:7890"
    scraper = DoubanCollaborationScraper(douban_url, proxy_url)
    results = scraper.get_all_collaborations_list()
