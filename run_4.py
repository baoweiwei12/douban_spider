import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from db import crud, database, schemas
from douban.requirement_4 import DoubanCollaborationScraper
from log import init_logger
from sqlalchemy.orm import Session


def scrape_task(
    task: schemas.Marking,
    db: Session,
    every_times_sleep: int = 2,
    proxy_url: str | None = None,
):
    logging.info(f"Scraping [{task.douban_person_id}] -- requirement_4 ")
    start_time = time.time()
    scraper = DoubanCollaborationScraper(task.douban_person_id, proxy_url)
    try:
        collaborations_list = scraper.get_all_collaborations_list(every_times_sleep)
        db_collaborations_list = crud.create_collaborations_mutil(
            db, collaborations_list
        )
        end_time = time.time()
        logging.info(
            f"Scraped {len(db_collaborations_list)} collaborations for [{task.douban_person_id}] in {end_time - start_time:.2f} seconds"
        )
        crud.change_marking_status(db, task.douban_person_id, "requirement_4", True)  # type: ignore

    except Exception as e:
        logging.error(f"Error occurred while scraping [{task.douban_person_id}]: {e}")


def main(
    task_nums: int = 1,
    seconds: int = 10,
    every_times_sleep: int = 2,
    proxy_url: str | None = None,
):
    # 配置logging
    init_logger("run[4]")
    db = database.SessionLocal()
    try:
        while True:
            unfinished_tasks = crud.get_unfinished_marking_mutil(
                db, "requirement_4", task_nums
            )
            if len(unfinished_tasks) == 0:
                logging.info("No unfinished tasks, exiting...")
                break

            with ThreadPoolExecutor(max_workers=task_nums) as executor:  # 调整线程数
                futures = [
                    executor.submit(scrape_task, task, db, every_times_sleep, proxy_url)
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
    # 任务数
    TASK_NUMS = 1
    # 每线程组休眠秒数
    SECONDS = 20
    # 每请求休眠秒数
    EVERY_TIMES_SLEEP = 2
    main(TASK_NUMS, SECONDS, EVERY_TIMES_SLEEP, PROXY_URL)
