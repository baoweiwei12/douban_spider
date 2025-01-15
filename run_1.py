import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from db import crud, database, schemas
from douban.requirement_1 import DoubanPersonScraper
from log import init_logger
import time
from sqlalchemy.orm import Session


def scrape_task(task: schemas.Marking, db: Session, proxy_url: str | None = None):
    logging.info(f"Scraping [{task.douban_person_id}]")
    person_scraper = DoubanPersonScraper(task.douban_person_id, proxy_url)
    try:
        person_info = person_scraper.scrape()
        new_person = crud.create_douban_person(db, person_info)
        if new_person is not None:
            logging.info(
                f"[{new_person.douban_id} - {new_person.douban_person_id}] Success"
            )
        else:
            logging.info(
                f"[[{person_info.douban_id} - {person_info.douban_person_id}] Already Exists"
            )
        crud.change_marking_status(db, person_info.douban_person_id, "requirement_1", True)  # type: ignore
    except Exception as e:
        logging.error(f"Error occurred while scraping [{task.douban_person_id}]: {e}")


def main(task_nums: int = 10, seconds: int = 20, proxy_url: str | None = None):
    # 配置logging
    init_logger("run[1]")
    db = database.SessionLocal()
    try:
        while True:

            unfinished_tasks = crud.get_unfinished_marking_mutil(
                db, "requirement_1", task_nums
            )
            if len(unfinished_tasks) == 0:
                logging.info("No unfinished tasks, exiting...")
                break

            with ThreadPoolExecutor(max_workers=task_nums) as executor:  # 调整线程数
                futures = [
                    executor.submit(scrape_task, task, db, proxy_url)
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
    # 设置参数
    TASK_NUMS = 1
    SECONDS = 20
    # PROXY_URL = "http://t13648913065383:zlti6qyj@o898.kdltps.com:15818"
    PROXY_URL = None
    main(TASK_NUMS, SECONDS, PROXY_URL)
