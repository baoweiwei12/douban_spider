from db import schemas, models
from sqlalchemy.orm import Session
from typing import Literal, Sequence
from sqlalchemy import func


def get_unfinished_marking(
    db: Session,
    filter: Literal[
        "requirement_1",
        "requirement_2",
        "requirement_3",
        "requirement_4",
    ],
):
    return (
        db.query(models.Marking)
        .filter(getattr(models.Marking, filter) == False)
        .order_by(func.random())
        .first()
    )


def change_marking_status(
    db: Session,
    douban_person_id: str,
    filter: Literal[
        "requirement_1",
        "requirement_2",
        "requirement_3",
        "requirement_4",
    ],
    status: bool,
):
    marking = (
        db.query(models.Marking)
        .filter(models.Marking.douban_person_id == douban_person_id)
        .first()
    )
    if marking is None:
        return None
    setattr(marking, filter, status)
    db.commit()
    db.refresh(marking)
    return marking


def get_unfinished_marking_mutil(
    db: Session,
    filter: Literal[
        "requirement_1",
        "requirement_2",
        "requirement_3",
        "requirement_4",
    ],
    limit: int,
):
    return (
        db.query(models.Marking)
        .filter(getattr(models.Marking, filter) == False)
        .order_by(func.random())
        .limit(limit)
        .all()
    )


def change_subject_marking_status(
    db: Session,
    douban_subject_id: str,
    filter: Literal[
        "requirement_5",
        "requirement_6",
        "requirement_7",
    ],
    status: bool,
):
    marking = (
        db.query(models.SubjectMarking)
        .filter(models.SubjectMarking.douban_subject_id == douban_subject_id)
        .first()
    )
    if marking is None:
        return None
    setattr(marking, filter, status)
    db.commit()
    db.refresh(marking)
    return marking


def get_unfinished_subject_marking_mutil(
    db: Session,
    filter: Literal[
        "requirement_5",
        "requirement_6",
        "requirement_7",
    ],
    limit: int,
    type: Literal["movie", "book", "music"] | None = None,
):
    query = db.query(models.SubjectMarking).filter(
        getattr(models.SubjectMarking, filter) == False
    )
    if type is not None:
        query = query.filter(models.SubjectMarking.type == type)
    return query.order_by(func.random()).limit(limit).all()


def create_douban_person(db: Session, douban_person: schemas.DoubanPersonCreate):
    if (
        db.query(models.DoubanPerson)
        .filter(models.DoubanPerson.douban_person_id == douban_person.douban_person_id)
        .first()
        is not None
    ):
        return None
    new_douban_person = models.DoubanPerson(**douban_person.model_dump())
    db.add(new_douban_person)
    db.commit()
    db.refresh(new_douban_person)
    return new_douban_person


def create_award_info_mutil(
    db: Session, award_info_list: Sequence[schemas.AwardInfoCreate]
):
    award_info_list = [
        models.AwardInfo(**award_info.model_dump()) for award_info in award_info_list
    ]
    db.add_all(award_info_list)
    db.commit()
    return award_info_list


def create_collaborations_mutil(
    db: Session, collaborations_list: Sequence[schemas.CollaborationInfoCreate]
):
    collaborations_list = [
        models.CollaborationInfo(**collaboration.model_dump())
        for collaboration in collaborations_list
    ]
    db.add_all(collaborations_list)
    db.commit()
    return collaborations_list


def create_douban_works_mutil(
    db: Session, works_list: Sequence[schemas.DoubanWorkCreate]
):
    works_list = [models.DoubanWork(**work.model_dump()) for work in works_list]
    db.add_all(works_list)
    db.commit()
    return works_list


def create_movie(db: Session, movie: schemas.MovieCreate):
    new_movie = models.Movie(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie


def create_book(db: Session, book: schemas.BookCreate):
    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


def create_music(db: Session, music: schemas.MusicCreate):
    new_music = models.Music(**music.model_dump())
    db.add(new_music)
    db.commit()
    db.refresh(new_music)
    return new_music


def create_subject_award(db: Session, subject_award: schemas.SubjectAwardCreate):
    new_subject_award = models.SubjectAward(**subject_award.model_dump())
    db.add(new_subject_award)
    db.commit()
    db.refresh(new_subject_award)
    return new_subject_award


def create_subject_awards_mutil(
    db: Session, subject_awards_list: Sequence[schemas.SubjectAwardCreate]
):
    subject_awards_list = [
        models.SubjectAward(**subject_award.model_dump())
        for subject_award in subject_awards_list
    ]
    db.add_all(subject_awards_list)
    db.commit()
    return subject_awards_list


def create_casts_mutil(db: Session, casts_list: Sequence[schemas.CastCreate]):
    casts_list = [models.Cast(**cast.model_dump()) for cast in casts_list]
    db.add_all(casts_list)
    db.commit()
    return casts_list
