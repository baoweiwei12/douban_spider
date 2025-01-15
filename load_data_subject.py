import pandas as pd
from db import models, database, schemas
from log import init_logger
import logging

init_logger("load_data_subject")
urls_data_path = "./data/subject_urls.csv"


df = pd.read_csv(urls_data_path)
urls = df["work_url"].tolist()

db = database.SessionLocal()

for url in urls:
    id = str(url.split("/")[-2])
    if "movie" in url:
        type = "movie"
    elif "book" in url:
        type = "book"
    else:
        type = "music"
    if (
        db.query(models.SubjectMarking)
        .filter(models.SubjectMarking.douban_subject_id == id)
        .first()
        is not None
    ):
        logging.warning(f"{id} already exists")
        continue
    new_marking = models.SubjectMarking(
        **(schemas.SubjectMarkingCreate(douban_subject_id=id, type=type).model_dump())
    )
    db.add(new_marking)
    db.commit()
    logging.info(f"{id} added")

db.close()
