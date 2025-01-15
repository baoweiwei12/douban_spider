import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from db import crud, database, schemas
from douban.requirement_5 import DoubanSubjectScraper
from log import init_logger
from sqlalchemy.orm import Session


def scrape_task(
    task: schemas.SubjectMarking,
    db: Session,
    proxy_url: str | None = None,
):
    logging.info(f"Scraping [{task.douban_subject_id}] -- requirement_5 ")
    start_time = time.time()
    scraper = DoubanSubjectScraper(task.douban_subject_id, task.type, proxy_url)
    try:

        if task.type == "movie":
            data = scraper._get_subject_movie()
            crud.create_movie(db, data)

        elif task.type == "book":
            data = scraper._get_subject_book()
            crud.create_book(db, data)

        elif task.type == "music":
            data = scraper._get_subject_music()
            crud.create_music(db, data)
        end_time = time.time()
        logging.info(
            f"Scraped {task.type} - [{task.douban_subject_id}] in {end_time - start_time:.2f} seconds"
        )
        crud.change_subject_marking_status(
            db, task.douban_subject_id, "requirement_5", True
        )

    except Exception as e:
        logging.error(
            f"Error occurred while scraping {task.type} - [{task.douban_subject_id}]: {e}"
        )


def main(
    task_nums: int = 1,
    seconds: int = 10,
    proxy_url: str | None = None,
):
    # 配置logging
    init_logger("run[5]")
    db = database.SessionLocal()
    try:
        while True:
            unfinished_tasks = crud.get_unfinished_subject_marking_mutil(
                db, "requirement_5", task_nums
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
    # 配置选项
    # PROXY_URL = "http://t13648913065383:zlti6qyj@o898.kdltps.com:15818"
    PROXY_URL = None
    # 任务数
    TASK_NUMS = 1
    # 每线程组休眠秒数
    SECONDS = 20

    main(TASK_NUMS, SECONDS, PROXY_URL)
