import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pydantic import BaseModel
from db import crud, database, schemas
from douban.requirement_3 import DoubanAwardScraper
from log import init_logger
from sqlalchemy.orm import Session
from cookies_manager import CookieRotator


def scrape_task(
    task: schemas.Marking,
    db: Session,
    rotator: CookieRotator,
    proxy_url: str | None = None,
):
    logging.info(f"Scraping [{task.douban_person_id}] -- requirement_3 ")
    award_scraper = DoubanAwardScraper(
        task.douban_person_id, proxy_url, rotator.get_next_cookie()
    )
    try:
        awards_list = award_scraper.get_awards_list()
        db_awards_list = crud.create_award_info_mutil(db, awards_list)
        logging.info(
            f"Scraped {len(db_awards_list)} awards for [{task.douban_person_id}]"
        )
        crud.change_marking_status(db, task.douban_person_id, "requirement_3", True)  # type: ignore
    except Exception as e:
        logging.error(f"Error occurred while scraping [{task.douban_person_id}]: {e}")


def main(
    cookies_list: list[dict],
    task_nums: int = 1,
    seconds: int = 10,
    proxy_url: str | None = None,
):
    # 配置logging
    init_logger("run[3]")
    # 实例化 CookieRotator
    rotator = CookieRotator(cookies_list)
    db = database.SessionLocal()
    try:
        while True:
            unfinished_tasks = crud.get_unfinished_marking_mutil(
                db, "requirement_3", task_nums
            )
            if len(unfinished_tasks) == 0:
                logging.info("No unfinished tasks, exiting...")
                break

            with ThreadPoolExecutor(max_workers=task_nums) as executor:  # 调整线程数
                futures = [
                    executor.submit(scrape_task, task, db, rotator, proxy_url)
                    for task in unfinished_tasks
                ]
                for future in as_completed(futures):
                    try:
                        future.result()  # 获取任务结果
                    except Exception as e:
                        logging.error(f"Error in task: {e}")
            logging.info(f"Sleeping for {seconds} seconds...")
            time.sleep(seconds)

    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting...")
    finally:
        db.close()


if __name__ == "__main__":
    # 配置选项
    # PROXY_URL = "http://t13648913065383:zlti6qyj@o898.kdltps.com:15818"
    PROXY_URL = None
    # cookies list
    COOKIES_LIST = [
        {
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
        },
    ]
    # 任务数
    TASK_NUMS = 1
    # 休眠秒数
    SECONDS = 20
    main(COOKIES_LIST, TASK_NUMS, SECONDS, PROXY_URL)
