from douban.requirement_1 import DoubanPersonScraper
from douban.requirement_4 import DoubanCollaborationScraper
from douban.requirement_6 import DoubanCastScraper


def test_1(id: str, proxy: str | None = None):
    scraper = DoubanPersonScraper(id, proxy)
    try:
        person = scraper.scrape()
        for key, value in person.model_dump().items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error during scraping: {e}")


def test4(id: str, proxy: str | None = None):
    scraper = DoubanCollaborationScraper(id, proxy)
    results = scraper.get_all_collaborations_list()
    for result in results:
        print(result.model_dump())


def test6(id: str, proxy: str | None = None):
    scraper = DoubanCastScraper(id, proxy)
    result = scraper.get_data()
    for i in result:
        print(i.model_dump())


if __name__ == "__main__":
    # test_1("30103490", "http://127.0.0.1:7890")
    # test4("34880873")
    test6("27042557")
