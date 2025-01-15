import re
import time
import requests
from bs4 import BeautifulSoup, Tag, ResultSet
from typing import Any, Callable, List, Union
from pydantic import BaseModel, Field
from typing import Optional, Literal
from retry import retry
from db.schemas import MovieCreate, BookCreate, MusicCreate
from lxml import etree
import utils


class DoubanSubjectScraper:

    def __init__(
        self,
        douban_subject_id: str,
        type: Literal["movie", "book", "music"],
        proxy_url: str | None = None,
    ):
        self.douban_subject_id = douban_subject_id
        self.type = type
        self.subject_url = f"https://{type}.douban.com/subject/{douban_subject_id}/"
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
            self.subject_url, headers=self.headers, proxies=self.proxies
        )
        response.raise_for_status()
        html = response.text
        return html

    def get_subject(self) -> Union[MovieCreate, BookCreate, MusicCreate]:
        map = {
            "movie": self._get_subject_movie,
            "book": self._get_subject_book,
            "music": self._get_subject_music,
        }
        # 根据 self.type 调用对应的函数并返回结果
        return map[self.type]()

    def _get_subject_movie(self) -> MovieCreate:
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        new_subject = MovieCreate()
        new_subject.title = (
            element.text
            if (element := soup.select_one("#content h1 span")) is not None
            else None
        )

        new_subject.subject_url = self.subject_url
        new_subject.year = (
            element.text.replace("(", "").replace(")", "")
            if (element := soup.select_one("#content h1 span:nth-of-type(2)"))
            is not None
            else None
        )
        new_subject.director = (
            element.text
            if (element := soup.select_one(".attrs a")) is not None
            else None
        )
        new_subject.director_url = (
            element.attrs.get("href")
            if (element := soup.select_one(".attrs a")) is not None
            else None
        )
        screenwriter_span = soup.find("span", class_="pl", string="编剧")
        if screenwriter_span is not None:
            screenwriter_attrs_span = screenwriter_span.find_next_sibling(
                "span", class_="attrs"
            )
            if screenwriter_attrs_span is not None:
                screenwriter_attrs_a = screenwriter_attrs_span.find_all("a")  # type: ignore
                new_subject.screenwriter = [a.text for a in screenwriter_attrs_a]
                new_subject.screenwriter_url = [
                    a.attrs.get("href", "") for a in screenwriter_attrs_a
                ]
        starring_span = soup.find("span", class_="pl", string="主演")
        if starring_span is not None:
            starring_attrs_span = starring_span.find_next_sibling(
                "span", class_="attrs"
            )
            if starring_attrs_span is not None:
                screenwriter_attrs_a = starring_attrs_span.find_all("a")  # type: ignore
                new_subject.starring = [a.text for a in screenwriter_attrs_a]
                new_subject.starring_url = [
                    a.attrs.get("href", "") for a in screenwriter_attrs_a
                ]

        type_span = soup.find("span", class_="pl", string="类型:")
        new_subject.genre = []
        if type_span is not None:
            for sibling in type_span.find_next_siblings("span", property="v:genre"):
                new_subject.genre.append(sibling.text)
        country_span = soup.find("span", class_="pl", string="制片国家/地区:")
        if country_span:
            # 获取 <span> 标签后面的文本
            new_subject.country = (
                elemnet.text.strip()
                if (elemnet := country_span.next_sibling) is not None
                else None
            )
        language_span = soup.find("span", class_="pl", string="语言:")
        if language_span:
            # 获取 <span> 标签后面的文本
            new_subject.language = (
                elemnet.text.strip()
                if (elemnet := language_span.next_sibling) is not None
                else None
            )
        release_date_elements = soup.find_all(property="v:initialReleaseDate")
        new_subject.release_date = [
            element.text.strip() for element in release_date_elements
        ]
        new_subject.runtime = (
            element.text.strip()
            if (element := soup.find("span", property="v:runtime")) is not None
            else None
        )
        episodes_span = soup.find("span", class_="pl", string="集数:")
        if episodes_span is not None:
            new_subject.episodes = (
                element.text.strip()
                if (element := episodes_span.next_sibling) is not None
                else None
            )
        episode_runtime_span = soup.find("span", class_="pl", string="单集片长:")
        if episode_runtime_span is not None:
            new_subject.episode_runtime = (
                element.text.strip()
                if (element := episode_runtime_span.next_sibling) is not None
                else None
            )
        aka_span = soup.find("span", class_="pl", string="又名:")
        if aka_span is not None:
            new_subject.aka = (
                element.text.strip()
                if (element := aka_span.next_sibling) is not None
                else None
            )
        imdb_span = soup.find("span", class_="pl", string="IMDb:")
        if imdb_span is not None:
            new_subject.imdb = (
                element.text.strip()
                if (element := imdb_span.next_sibling) is not None
                else None
            )
        new_subject.synopsis = (
            element.text.strip()
            if (element := soup.find("span", property="v:summary")) is not None
            else None
        )
        celebrities_span = soup.find("div", id="celebrities")
        if celebrities_span:
            cast_count_span = celebrities_span.find("a")
            if cast_count_span:
                new_subject.cast_count = cast_count_span.text.replace("全部 ", "")  # type: ignore
                new_subject.cast_details_url = f"{self.subject_url}celebrities"
        if soup.find("i", string=re.compile("获奖情况")):
            new_subject.awards_url = f"{self.subject_url}awards/"
        new_subject.douban_rating = (
            element.text.strip()
            if (element := soup.find("strong", property="v:average")) is not None
            else None
        )
        new_subject.rating_count = (
            element.text.strip()
            if (element := soup.find("span", property="v:votes")) is not None
            else None
        )
        count_div = soup.find("div", class_="subject-others-interests-ft")
        if isinstance(count_div, Tag):
            new_subject.watching_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=N",
                    )
                )
                is not None
                else None
            )
            new_subject.watched_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=P",
                    )
                )
                is not None
                else None
            )
            new_subject.want_to_watch_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=F",
                    )
                )
                is not None
                else None
            )
        ratio_spans = soup.find_all("span", class_="rating_per")
        if len(ratio_spans) >= 5:
            (
                new_subject.five_star_ratio,
                new_subject.four_star_ratio,
                new_subject.three_star_ratio,
                new_subject.two_star_ratio,
                new_subject.one_star_ratio,
            ) = [span.text for span in ratio_spans]
        comments_section = soup.find("div", id="comments-section")

        if isinstance(comments_section, Tag):
            new_subject.short_comment_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := comments_section.find(
                        "a",
                        href=f"{self.subject_url}comments?status=P",
                    )
                )
                is not None
                else None
            )
            new_subject.short_comment_url = f"{self.subject_url}comments?status=P"
        reviews_wrapper = soup.find("section", id="reviews-wrapper")
        if isinstance(reviews_wrapper, Tag):
            new_subject.review_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := reviews_wrapper.find(
                        "a",
                        href="reviews",
                    )
                )
                is not None
                else None
            )
            new_subject.review_url = f"{self.subject_url}reviews"
        section_discussion = soup.find("div", class_="section-discussion")
        if isinstance(section_discussion, Tag):
            new_subject.discussion_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := section_discussion.find(
                        "a", href=f"/subject/{self.douban_subject_id}/discussion/"
                    )
                )
                is not None
                else None
            )
            new_subject.discussion_url = f"{self.subject_url}discussion/"
        askmatrix = soup.find("div", id="askmatrix")
        if isinstance(askmatrix, Tag):
            new_subject.question_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := askmatrix.find(
                        "a", href=f"{self.subject_url}questions/?from=subject"
                    )
                )
                is not None
                else None
            )
            new_subject.question_url = f"{self.subject_url}questions/?from=subject"
        return new_subject

    def _get_next_a(self, soup: BeautifulSoup, key: str):
        try:
            tag = soup.find("span", string=key).find_next("a")  # type: ignore
            return (
                (tag.text, tag.attrs.get("href"))
                if isinstance(tag, Tag)
                else (None, None)
            )
        except AttributeError:
            return (None, None)

    def _get_next_text(self, soup: BeautifulSoup, key: str):
        try:
            tag = soup.find("span", string=key)  # type: ignore
            if not isinstance(tag, Tag):
                return None
            if tag.next_sibling is None:
                return None
            return tag.next_sibling.text.strip()
        except AttributeError:
            return None

    def _get_subject_book(self) -> BookCreate:
        new_subject = BookCreate()
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        new_subject.title = (
            element.text
            if (element := soup.find("span", property="v:itemreviewed")) is not None
            else None
        )
        try:
            new_subject.subject_url = self.subject_url
            author_a_list = soup.find("div", id="info").find("span").find_all("a")  # type: ignore
            new_subject.author = [a.text for a in author_a_list]
            new_subject.author_url = [
                "https://book.douban.com" + a.attrs.get("href") for a in author_a_list
            ]
        except AttributeError:
            pass

        new_subject.publisher, new_subject.publisher_url = self._get_next_a(
            soup, "出版社:"
        )

        new_subject.producer, new_subject.producer_url = self._get_next_a(
            soup, "出品方:"
        )
        try:
            new_subject.original_title = soup.find(
                "span", class_="pl", string="原作名:"
            ).next_sibling.text.strip()  # type: ignore
        except AttributeError:
            pass
        new_subject.translator, new_subject.translator_url = self._get_next_a(
            soup, " 译者"
        )
        new_subject.publication_year = self._get_next_text(soup, "出版年:")
        new_subject.pages = self._get_next_text(soup, "页数:")
        new_subject.binding = self._get_next_text(soup, "装帧:")
        new_subject.series, new_subject.series_url = self._get_next_a(soup, "丛书:")
        new_subject.isbn = self._get_next_text(soup, "ISBN:")
        new_subject.synopsis = "".join(soup.find("span", class_="all hidden").text.split())  # type: ignore
        try:
            new_subject.author_intro = soup.find("p", string="【编者简介】").find_next("p").text.strip()  # type: ignore
            new_subject.author_intro += soup.find("p", string="【译者简介】").find_next("p").text.strip()  # type: ignore
        except AttributeError:
            pass
        try:
            new_subject.table_of_contents = "".join([i + "/" for i in soup.find("div", id=f"dir_{self.douban_subject_id}_full").text.replace("·", "").replace("(收起)", "").split()])  # type: ignore
        except AttributeError:
            pass
        new_subject.series_info = (
            e.text.replace("\n", "").replace(" ", "").replace("·", "").strip()
            if isinstance((e := soup.find("div", class_="subject_show block5")), Tag)
            else None
        )

        new_subject.douban_rating = (
            element.text.strip()
            if (element := soup.find("strong", property="v:average")) is not None
            else None
        )
        new_subject.rating_count = (
            element.text.strip()
            if (element := soup.find("span", property="v:votes")) is not None
            else None
        )
        count_div = soup.find("div", id="collector")
        if isinstance(count_div, Tag):
            new_subject.reading_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=N",
                    )
                )
                is not None
                else None
            )
            new_subject.read_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=P",
                    )
                )
                is not None
                else None
            )
            new_subject.want_to_read_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=F",
                    )
                )
                is not None
                else None
            )
        ratio_spans = soup.find_all("span", class_="rating_per")
        (
            new_subject.five_star_ratio,
            new_subject.four_star_ratio,
            new_subject.three_star_ratio,
            new_subject.two_star_ratio,
            new_subject.one_star_ratio,
        ) = [span.text for span in ratio_spans]
        comments_section = soup.find("div", id="comments-section")

        if isinstance(comments_section, Tag):
            new_subject.short_comment_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := comments_section.find(
                        "a",
                        href=f"{self.subject_url}comments/",
                    )
                )
                is not None
                else None
            )
            new_subject.short_comment_url = f"{self.subject_url}comments/"
        reviews_wrapper = soup.find("section", id="reviews-wrapper")
        if isinstance(reviews_wrapper, Tag):
            new_subject.review_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := reviews_wrapper.find(
                        "a",
                        href="reviews",
                    )
                )
                is not None
                else None
            )
            new_subject.review_url = f"{self.subject_url}reviews"
        new_subject.reading_note_url = f"{self.subject_url}annotation"
        return new_subject

    def _get_subject_music(self):
        new_subject = MusicCreate()
        html = self._get_html()
        soup = BeautifulSoup(html, "html.parser")
        new_subject.title = (
            element.text
            if (element := soup.select_one("#wrapper > h1 > span")) is not None
            else None
        )
        new_subject.subject_url = self.subject_url
        new_subject.aka = self._get_next_text(soup, "又名:")
        performer_a_list = soup.select("#info > span:nth-child(3) > span a")
        new_subject.performer = (
            [performer_a.text for performer_a in performer_a_list]
            if performer_a_list
            else None
        )
        new_subject.performer_url = (
            [performer_a.attrs.get("href", "") for performer_a in performer_a_list]
            if performer_a_list
            else None
        )
        new_subject.genre = self._get_next_text(soup, "流派:")
        new_subject.album_type = self._get_next_text(soup, "专辑类型:")
        new_subject.medium = self._get_next_text(soup, "介质:")
        new_subject.release_date = self._get_next_text(soup, "发行时间:")
        new_subject.publisher = self._get_next_text(soup, "出版者:")
        new_subject.disc_count = self._get_next_text(soup, "唱片数:")
        new_subject.barcode = self._get_next_text(soup, "条形码:")
        new_subject.douban_rating = (
            element.text.strip()
            if (element := soup.find("strong", property="v:average")) is not None
            else None
        )
        new_subject.related_movie, new_subject.related_movie_url = self._get_next_a(
            soup, "相关电影:"
        )
        new_subject.synopsis = "".join(soup.find("span", class_="all hidden").text.split())  # type: ignore
        track_li_list = soup.select(".track-items.indent li")
        new_subject.track_list = [track_li.text for track_li in track_li_list]
        new_subject.rating_count = (
            element.text.strip()
            if (element := soup.find("span", property="v:votes")) is not None
            else None
        )
        count_div = soup.find("div", id="collector")
        if isinstance(count_div, Tag):
            new_subject.listening_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=N",
                    )
                )
                is not None
                else None
            )
            new_subject.listened_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=P",
                    )
                )
                is not None
                else None
            )
            new_subject.want_to_listen_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := count_div.find(
                        "a",
                        href=f"{self.subject_url}comments?status=F",
                    )
                )
                is not None
                else None
            )
        ratio_spans = soup.find_all("span", class_="rating_per")
        (
            new_subject.five_star_ratio,
            new_subject.four_star_ratio,
            new_subject.three_star_ratio,
            new_subject.two_star_ratio,
            new_subject.one_star_ratio,
        ) = [span.text for span in ratio_spans]
        comments_section = soup.find("div", id="comments-section")

        if isinstance(comments_section, Tag):
            new_subject.short_comment_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := comments_section.find(
                        "a",
                        href=f"{self.subject_url}comments/",
                    )
                )
                is not None
                else None
            )
            new_subject.short_comment_url = f"{self.subject_url}comments/"
        reviews_wrapper = soup.find("section", id="reviews-wrapper")
        if isinstance(reviews_wrapper, Tag):
            new_subject.review_count = (
                utils.extract_numbers(element.text)[0]
                if (
                    element := reviews_wrapper.find(
                        "a",
                        href="reviews",
                    )
                )
                is not None
                else None
            )
            new_subject.review_url = f"{self.subject_url}reviews"
        # new_subject.reading_note_url = f"{self.subject_url}annotation"
        return new_subject


if __name__ == "__main__":

    scraper = DoubanSubjectScraper("33456213", "movie")
    result = scraper.get_subject()

    for key, value in result.model_dump().items():
        print(f"{key}:{value}")
