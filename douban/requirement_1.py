import re
from bs4 import BeautifulSoup
import requests
from lxml import etree
from pydantic import BaseModel, Field
from typing import Optional
from db.schemas import DoubanPerson
from retry import retry


class DoubanPersonScraper:

    def __init__(self, douban_person_id: str, proxy_url: Optional[str] = None):
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
        self.html = ""

    @retry(tries=3, delay=2, backoff=2)
    def get_home_page(self):
        response = requests.get(
            self.douban_url, headers=self.headers, proxies=self.proxies
        )
        response.raise_for_status()
        self.html = response.text

    @retry(tries=3, delay=2, backoff=2)
    def get_works_count(self) -> Optional[str]:
        url = self.douban_url + "creations?sortby=collection&type=filmmaker"
        response = requests.get(url, headers=self.headers, proxies=self.proxies)
        response.raise_for_status()
        html = response.text
        dom = etree.HTML(html)  # type: ignore
        h1_element = dom.xpath('//*[@id="content"]/h1')
        if h1_element:
            h1_text = h1_element[0].text
            number = re.search(r"\((\d+)\)", h1_text)
            return number.group().replace("(", "").replace(")", "") if number else None
        return None

    @retry(tries=3, delay=2, backoff=2)
    def get_co_star_count(self) -> Optional[str]:
        params = {
            "start": "0",
            "count": "10",
            "name": "",
            "simple": "0",
        }
        response = requests.get(
            f"https://m.douban.com/rexxar/api/v2/elessar/subject/{self.douban_url.split('/')[-2]}/partners",
            params=params,
            headers=self.headers,
            proxies=self.proxies,
        )
        response.raise_for_status()
        return str(response.json()["total"])

    def scrape(self) -> DoubanPerson:
        if self.html == "":
            self.get_home_page()

        soup = BeautifulSoup(self.html, "html.parser")

        douban_id_element = soup.select_one(".subject-name")
        douban_id = douban_id_element.text if douban_id_element else None

        target_fields = [
            "性别",
            "出生日期",
            "出生地",
            "更多外文名",
            "家庭成员",
            "IMDb编号",
            "职业",
        ]
        subject_info = {}
        for li in soup.select(".subject-property li"):
            label = li.select_one(".label")
            value = li.select_one(".value")
            if label and value:
                key = label.text.strip().replace(":", "")
                if key in target_fields:
                    subject_info[key] = value.text.strip()

        gender = subject_info.get("性别", None)
        birth_date = subject_info.get("出生日期", None)
        birth_place = subject_info.get("出生地", None)
        more_foreign_names = subject_info.get("更多外文名", None)
        family_members = subject_info.get("家庭成员", None)
        imdb_id = subject_info.get("IMDb编号", None)
        occupation = subject_info.get("职业", None)

        douban_followers_elemt = soup.select_one("#fans_count")
        douban_followers = (
            douban_followers_elemt.text if douban_followers_elemt else None
        )

        introduction_element = soup.select("div.desc div.content p")
        introduction = "".join(
            p.get_text(strip=True)
            for p in introduction_element
            if p.get_text(strip=True)
        )

        image_link = soup.find("a", href="photos")
        image_count = re.search(r"\d+", image_link.get_text()) if image_link else None
        homepage_pictures_count = image_count.group() if image_count else None

        awards_count_element = soup.select_one('a[href*="awards"]')
        awards_count = None
        if awards_count_element:
            awards_count_text = awards_count_element.get_text()
            awards_count_match = re.search(r"(\d+)", awards_count_text)
            awards_count = awards_count_match.group() if awards_count_match else None

        homepage_contributors_element = soup.select_one('a[href*="contributors"]')
        homepage_contributors = None
        if homepage_contributors_element:
            homepage_contributors_text = homepage_contributors_element.get_text()
            homepage_contributors_match = re.search(
                r"(\d+)", homepage_contributors_text
            )
            homepage_contributors = (
                homepage_contributors_match.group()
                if homepage_contributors_match
                else None
            )

        return DoubanPerson(
            douban_person_id=self.douban_person_id,
            douban_url=self.douban_url,
            douban_id=douban_id,
            gender=gender,
            birth_date=birth_date,
            birth_place=birth_place,
            more_foreign_names=more_foreign_names,
            family_members=family_members,
            imdb_id=imdb_id,
            occupation=occupation,
            douban_followers=douban_followers,
            douban_followers_url=self.douban_url + "followers",
            introduction=introduction,
            homepage_pictures_count=homepage_pictures_count,
            homepage_pictures_url=self.douban_url + "photos/",
            works_count=self.get_works_count(),
            works_url=self.douban_url + "creations?sortby=time&type=filmmaker",
            awards_count=awards_count,
            awards_url=self.douban_url + "awards",
            co_star_count=self.get_co_star_count(),
            co_star_url=self.douban_url + "partners",
            homepage_contributors=homepage_contributors,
            homepage_contributors_url=self.douban_url + "contributors",
        )


if __name__ == "__main__":

    # 使用示例
    douban_url = "27246769"
    scraper = DoubanPersonScraper(douban_url, "http://127.0.0.1:7890")
    try:
        person = scraper.scrape()
        for key, value in person.model_dump().items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error during scraping: {e}")
