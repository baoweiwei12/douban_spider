from sqlalchemy import (
    JSON,
    TEXT,
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
from db.database import engine

Base = declarative_base()


class Marking(Base):
    __tablename__ = "marking"

    douban_person_id = Column(String(20), primary_key=True, comment="豆瓣人物id")
    requirement_1 = Column(
        Boolean, nullable=False, default=False, comment="任务1是否完成"
    )
    requirement_2 = Column(
        Boolean, nullable=False, default=False, comment="任务2是否完成"
    )
    requirement_3 = Column(
        Boolean, nullable=False, default=False, comment="任务3是否完成"
    )
    requirement_4 = Column(
        Boolean, nullable=False, default=False, comment="任务4是否完成"
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SubjectMarking(Base):
    __tablename__ = "subject_marking"
    douban_subject_id = Column(String(20), primary_key=True, comment="豆瓣作品id")
    type = Column(String, nullable=False, comment="作品类型")
    requirement_5 = Column(
        Boolean, nullable=False, default=False, comment="任务5是否完成"
    )
    requirement_6 = Column(
        Boolean, nullable=False, default=False, comment="任务6是否完成"
    )
    requirement_7 = Column(
        Boolean, nullable=False, default=False, comment="任务7是否完成"
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DoubanPerson(Base):
    __tablename__ = "douban_person"

    douban_person_id = Column(String(20), primary_key=True, comment="豆瓣人物id")
    douban_url = Column(String, nullable=True, comment="豆瓣URL")
    douban_id = Column(String, nullable=True, comment="豆瓣ID")
    gender = Column(String, nullable=True, comment="性别")
    birth_date = Column(String, nullable=True, comment="出生日期")
    birth_place = Column(String, nullable=True, comment="出生地")
    more_foreign_names = Column(String, nullable=True, comment="更多外文名")
    family_members = Column(String, nullable=True, comment="家庭成员")
    imdb_id = Column(String, nullable=True, comment="IMDb编号")
    occupation = Column(String, nullable=True, comment="职业")
    douban_followers = Column(String, nullable=True, comment="豆瓣关注人数")
    douban_followers_url = Column(String, nullable=True, comment="豆瓣关注人列表URL")
    introduction = Column(String, nullable=True, comment="人物简介")
    homepage_pictures_count = Column(String, nullable=True, comment="主页图片张数")
    homepage_pictures_url = Column(String, nullable=True, comment="明星图片URL")
    works_count = Column(String, nullable=True, comment="作品个数")
    works_url = Column(String, nullable=True, comment="明星作品页URL")
    awards_count = Column(String, nullable=True, comment="获奖次数")
    awards_url = Column(String, nullable=True, comment="明星获奖情况URL")
    co_star_count = Column(String, nullable=True, comment="合作过的人物个数")
    co_star_url = Column(String, nullable=True, comment="明星合作人物档案URL")
    homepage_contributors = Column(String, nullable=True, comment="主页贡献者")
    homepage_contributors_url = Column(
        String, nullable=True, comment="主页贡献者档案URL"
    )


class AwardInfo(Base):
    __tablename__ = "award_info"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="id")
    douban_person_id = Column(String(20), comment="豆瓣人物id")
    douban_url = Column(String, nullable=True, comment="豆瓣URL")
    star_award_url = Column(String, nullable=True, comment="明星获奖情况URL")
    year = Column(String, nullable=True, comment="年份")
    award_name = Column(String, nullable=True, comment="奖名")
    award_name_url = Column(String, nullable=True, comment="奖名URL")
    specific_award = Column(String, nullable=True, comment="具体奖项")
    award_work = Column(String, nullable=True, comment="获奖作品")
    work_homepage_url = Column(String, nullable=True, comment="作品主页URL")


class CollaborationInfo(Base):
    __tablename__ = "collaboration_info"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    douban_person_id = Column(String, nullable=False, comment="豆瓣人物ID")
    douban_url = Column(String, nullable=True, comment="豆瓣URL")
    collaboration_url = Column(String, nullable=True, comment="合作人物档案URL")
    collaborator_name = Column(String, nullable=True, comment="合作人物姓名")
    collaborator_homepage_url = Column(String, nullable=True, comment="合作人物主页URL")
    collaborator_profession = Column(String, nullable=True, comment="合作人物职业")
    collaboration_count = Column(Integer, nullable=True, comment="合作作品数量")
    collaboration_works = Column(JSON, default=[], comment="合作作品列表")
    collaboration_works_homepage_url = Column(
        JSON, default=[], comment="合作作品主页URL列表"
    )
    collaborator_douban_followers = Column(
        Integer, nullable=True, comment="合作人物豆瓣关注人数"
    )


class DoubanWork(Base):
    __tablename__ = "douban_work"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    douban_person_id = Column(String, nullable=False, comment="豆瓣人物ID")
    douban_url = Column(String, nullable=True, comment="豆瓣URL")
    star_work_url = Column(String, nullable=True, comment="明星作品页URL")
    work_type = Column(String, nullable=True, comment="作品类型")
    work_name = Column(String, nullable=True, comment="作品名称")
    work_url = Column(String, nullable=True, comment="作品主页URL")
    year = Column(String, nullable=True, comment="年份")
    status = Column(String, nullable=True, comment="状态")
    role = Column(String, nullable=True, comment="担任")
    director = Column(String, nullable=True, comment="导演")
    actors = Column(String, nullable=True, comment="主演")
    author = Column(String, nullable=True, comment="作者")
    publisher = Column(String, nullable=True, comment="出版社")
    performer = Column(String, nullable=True, comment="表演者")
    rating = Column(String, nullable=True, comment="评分")
    rating_count = Column(String, nullable=True, comment="评价人数")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, comment="主键ID")
    title = Column(String(255), nullable=True, comment="作品名称")
    subject_url = Column(String(255), nullable=True, comment="作品页URL")
    year = Column(String(4), nullable=True, comment="年份")
    director = Column(String(255), nullable=True, comment="导演")
    director_url = Column(String(255), nullable=True, comment="导演-明星主页URL")
    screenwriter = Column(JSON, nullable=True, comment="编剧")
    screenwriter_url = Column(JSON, nullable=True, comment="编剧-明星主页URL")
    starring = Column(JSON, nullable=True, comment="主演")
    starring_url = Column(JSON, nullable=True, comment="主演-明星主页URL")
    genre = Column(JSON, nullable=True, comment="类型")
    country = Column(String(255), nullable=True, comment="制片国家/地区")
    language = Column(String(255), nullable=True, comment="语言")
    release_date = Column(
        JSON, nullable=True, comment="上映日期（电影）/首播（真人秀/电视剧）"
    )
    runtime = Column(String(50), nullable=True, comment="片长")
    episodes = Column(String(50), nullable=True, comment="集数")
    episode_runtime = Column(String(50), nullable=True, comment="单集片长")
    aka = Column(String(255), nullable=True, comment="又名")
    imdb = Column(String(50), nullable=True, comment="IMDb")
    synopsis = Column(JSON, nullable=True, comment="简介")
    cast_count = Column(String(50), nullable=True, comment="演职人员个数")
    cast_details_url = Column(String(255), nullable=True, comment="作品演职员详情URL")
    awards_url = Column(String(255), nullable=True, comment="作品获奖情况URL")
    douban_rating = Column(String(50), nullable=True, comment="豆瓣评分")
    rating_count = Column(String(50), nullable=True, comment="评价人数")
    watching_count = Column(String(50), nullable=True, comment="在看人数")
    watched_count = Column(String(50), nullable=True, comment="看过人数")
    want_to_watch_count = Column(String(50), nullable=True, comment="想看人数")
    five_star_ratio = Column(String(50), nullable=True, comment="5星占比")
    four_star_ratio = Column(String(50), nullable=True, comment="4星占比")
    three_star_ratio = Column(String(50), nullable=True, comment="3星占比")
    two_star_ratio = Column(String(50), nullable=True, comment="2星占比")
    one_star_ratio = Column(String(50), nullable=True, comment="1星占比")
    short_comment_count = Column(String(50), nullable=True, comment="短评条数")
    short_comment_url = Column(String(255), nullable=True, comment="短评列表URL")
    review_count = Column(String(50), nullable=True, comment="影评/剧评条数")
    review_url = Column(String(255), nullable=True, comment="影评/剧评列表URL")
    discussion_count = Column(String(50), nullable=True, comment="讨论区/小组讨论条数")
    discussion_url = Column(
        String(255), nullable=True, comment="讨论区/小组讨论列表URL"
    )
    question_count = Column(String(50), nullable=True, comment="问题个数")
    question_url = Column(String(255), nullable=True, comment="问题列表URL")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, comment="主键ID")
    title = Column(String(255), nullable=True, comment="作品名称")
    subject_url = Column(String(255), nullable=True, comment="作品页URL")
    author = Column(JSON, nullable=True, comment="作者")
    author_url = Column(JSON, nullable=True, comment="作者-明星主页URL")
    publisher = Column(String(255), nullable=True, comment="出版社")
    publisher_url = Column(String(255), nullable=True, comment="出版社主页URL")
    producer = Column(String(255), nullable=True, comment="出品方")
    producer_url = Column(String(255), nullable=True, comment="出品方主页URL")
    original_title = Column(String(255), nullable=True, comment="原作名")
    translator = Column(String(255), nullable=True, comment="译者")
    translator_url = Column(String(255), nullable=True, comment="译者主页URL")
    publication_year = Column(String(4), nullable=True, comment="出版年")
    pages = Column(String(50), nullable=True, comment="页数")
    binding = Column(String(50), nullable=True, comment="装帧")
    series = Column(String(255), nullable=True, comment="丛书")
    series_url = Column(String(255), nullable=True, comment="丛书主页URL")
    isbn = Column(String(50), nullable=True, comment="ISBN")
    synopsis = Column(JSON, nullable=True, comment="内容简介")
    author_intro = Column(JSON, nullable=True, comment="作者简介")
    table_of_contents = Column(JSON, nullable=True, comment="目录")
    series_info = Column(JSON, nullable=True, comment="丛书信息")
    douban_rating = Column(String(50), nullable=True, comment="豆瓣评分")
    rating_count = Column(String(50), nullable=True, comment="评价人数")
    reading_count = Column(String(50), nullable=True, comment="在读人数")
    read_count = Column(String(50), nullable=True, comment="读过人数")
    want_to_read_count = Column(String(50), nullable=True, comment="想读人数")
    five_star_ratio = Column(String(50), nullable=True, comment="5星占比")
    four_star_ratio = Column(String(50), nullable=True, comment="4星占比")
    three_star_ratio = Column(String(50), nullable=True, comment="3星占比")
    two_star_ratio = Column(String(50), nullable=True, comment="2星占比")
    one_star_ratio = Column(String(50), nullable=True, comment="1星占比")
    short_comment_count = Column(String(50), nullable=True, comment="短评条数")
    short_comment_url = Column(String(255), nullable=True, comment="短评列表URL")
    review_count = Column(String(50), nullable=True, comment="书评条数")
    review_url = Column(String(255), nullable=True, comment="书评列表URL")
    reading_note_count = Column(String(50), nullable=True, comment="读书笔记条数")
    reading_note_url = Column(String(255), nullable=True, comment="读书笔记列表URL")


class Music(Base):
    __tablename__ = "musics"

    id = Column(Integer, primary_key=True, comment="主键ID")
    title = Column(String(255), nullable=True, comment="作品名称")
    subject_url = Column(String(255), nullable=True, comment="作品页URL")
    aka = Column(String(255), nullable=True, comment="又名")
    performer = Column(JSON, nullable=True, comment="表演者")
    performer_url = Column(JSON, nullable=True, comment="表演者-明星主页URL")
    genre = Column(String(255), nullable=True, comment="流派")
    album_type = Column(String(50), nullable=True, comment="专辑类型")
    medium = Column(String(50), nullable=True, comment="介质")
    release_date = Column(String(50), nullable=True, comment="发行时间")
    publisher = Column(String(255), nullable=True, comment="出版者")
    disc_count = Column(String(50), nullable=True, comment="唱片数")
    barcode = Column(String(50), nullable=True, comment="条形码")
    related_movie = Column(String(255), nullable=True, comment="相关电影")
    related_movie_url = Column(
        String(255), nullable=True, comment="相关电影-作品主页URL"
    )
    synopsis = Column(JSON, nullable=True, comment="简介")
    track_list = Column(JSON, nullable=True, comment="曲目")
    douban_rating = Column(String(50), nullable=True, comment="豆瓣评分")
    rating_count = Column(String(50), nullable=True, comment="评价人数")
    listening_count = Column(String(50), nullable=True, comment="在听人数")
    listened_count = Column(String(50), nullable=True, comment="听过人数")
    want_to_listen_count = Column(String(50), nullable=True, comment="想听人数")
    five_star_ratio = Column(String(50), nullable=True, comment="5星占比")
    four_star_ratio = Column(String(50), nullable=True, comment="4星占比")
    three_star_ratio = Column(String(50), nullable=True, comment="3星占比")
    two_star_ratio = Column(String(50), nullable=True, comment="2星占比")
    one_star_ratio = Column(String(50), nullable=True, comment="1星占比")
    short_comment_count = Column(String(50), nullable=True, comment="短评条数")
    short_comment_url = Column(String(255), nullable=True, comment="短评列表URL")
    review_count = Column(String(50), nullable=True, comment="乐评条数")
    review_url = Column(String(255), nullable=True, comment="乐评列表URL")


class SubjectAward(Base):
    __tablename__ = "subject_awards"

    id = Column(Integer, primary_key=True, comment="主键ID")
    title = Column(String(255), nullable=True, comment="作品名称")
    award_url = Column(String(255), nullable=True, comment="作品获奖情况URL")
    year = Column(String(10), nullable=True, comment="年份")
    award_name = Column(String(255), nullable=True, comment="奖名")
    award_name_url = Column(String(255), nullable=True, comment="奖名URL")
    specific_award = Column(String(255), nullable=True, comment="具体奖项")
    winner = Column(TEXT, nullable=True, comment="获奖人")
    winner_url = Column(TEXT, nullable=True, comment="获奖人-明星主页URL")


class Cast(Base):
    __tablename__ = "casts"

    id = Column(Integer, primary_key=True, comment="主键ID")
    douban_subject_id = Column(String(50), nullable=True, comment="作品ID")
    title = Column(String(255), nullable=True, comment="作品名称")
    cast_list_url = Column(String(255), nullable=True, comment="作品演职员列表URL")
    role_category = Column(String(255), nullable=True, comment="职位类别")
    cast_name = Column(String(255), nullable=True, comment="演职员姓名")
    cast_url = Column(String(255), nullable=True, comment="演职员-明星主页URL")
    order = Column(String(50), nullable=True, comment="顺序排位")
    specific_role = Column(String(255), nullable=True, comment="具体职位")
    representative_work = Column(TEXT, nullable=True, comment="代表作")
    representative_work_url = Column(TEXT, nullable=True, comment="代表作-作品主页URL")


# 创建表
Base.metadata.create_all(engine)
