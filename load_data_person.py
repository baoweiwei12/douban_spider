import pandas as pd
from db import models, database, schemas
from log import init_logger
import logging

init_logger("load_data_person")
person_urls_data_path = "./data/person_urls.xlsx"


df = pd.read_excel(person_urls_data_path)
urls = df["豆瓣ID"].tolist()

db = database.SessionLocal()

for url in urls:
    id = str(url.split("/")[-2])
    if (
        db.query(models.Marking).filter(models.Marking.douban_person_id == id).first()
        is not None
    ):
        logging.warning(f"{id} already exists")
        continue
    new_marking = models.Marking(
        **(schemas.MarkingCreate(douban_person_id=id).model_dump())
    )
    db.add(new_marking)
    db.commit()
    logging.info(f"{id} added")

db.close()
