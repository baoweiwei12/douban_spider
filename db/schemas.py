from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class MarkingCreate(BaseModel):
    douban_person_id: str
    requirement_1: bool = False
    requirement_2: bool = False
    requirement_3: bool = False
    requirement_4: bool = False


class Marking(MarkingCreate):
    created_at: datetime
    updated_at: datetime

    class config:
        from_attributes = True


class SubjectMarkingCreate(BaseModel):
    douban_subject_id: str
    type: Literal["movie", "book", "music"]
    requirement_5: bool = False
    requirement_6: bool = False
    requirement_7: bool = False


class SubjectMarking(SubjectMarkingCreate):
    created_at: datetime
    updated_at: datetime

    class config:
        from_attributes = True


class DoubanPersonCreate(BaseModel):
    douban_person_id: str
    douban_url: str
    douban_id: Optional[str] = Field(default=None, description="豆瓣ID")
    gender: Optional[str] = Field(default=None, description="性别")
    birth_date: Optional[str] = Field(default=None, description="出生日期")
    birth_place: Optional[str] = Field(default=None, description="出生地")
    more_foreign_names: Optional[str] = Field(default=None, description="更多外文名")
    family_members: Optional[str] = Field(default=None, description="家庭成员")
    imdb_id: Optional[str] = Field(default=None, description="IMDb编号")
    occupation: Optional[str] = Field(default=None, description="职业")
    douban_followers: Optional[str] = Field(default=None, description="豆瓣关注人数")
    douban_followers_url: Optional[str] = Field(
        default=None, description="豆瓣关注人列表URL"
    )
    introduction: Optional[str] = Field(default=None, description="人物简介")
    homepage_pictures_count: Optional[str] = Field(
        default=None, description="主页图片张数"
    )
    homepage_pictures_url: Optional[str] = Field(
        default=None, description="明星图片URL"
    )
    works_count: Optional[str] = Field(default=None, description="作品个数")
    works_url: Optional[str] = Field(default=None, description="明星作品页URL")
    awards_count: Optional[str] = Field(default=None, description="获奖次数")
    awards_url: Optional[str] = Field(default=None, description="明星获奖情况URL")
    co_star_count: Optional[str] = Field(default=None, description="合作过的人物个数")
    co_star_url: Optional[str] = Field(default=None, description="明星合作人物档案URL")
    homepage_contributors: Optional[str] = Field(default=None, description="主页贡献者")
    homepage_contributors_url: Optional[str] = Field(
        None, description="主页贡献者档案URL"
    )


class DoubanPerson(DoubanPersonCreate):
    pass

    class config:
        from_attributes = True


class AwardInfoCreate(BaseModel):
    douban_person_id: str
    douban_url: str | None = Field(default=None, description="豆瓣URL")
    star_award_url: str | None = Field(default=None, description="明星获奖情况URL")
    year: str | None = Field(default=None, description="年份")
    award_name: str | None = Field(default=None, description="奖名")
    award_name_url: str | None = Field(default=None, description="奖名URL")
    specific_award: str | None = Field(default=None, description="具体奖项")
    award_work: str | None = Field(default=None, description="获奖作品")
    work_homepage_url: str | None = Field(default=None, description="作品主页URL")


class AwardInfo(AwardInfoCreate):
    pass
    id: int

    class config:
        from_attributes = True


class CollaborationInfoCreate(BaseModel):
    douban_person_id: str
    douban_url: str | None = Field(default=None, description="豆瓣URL")
    collaboration_url: str | None = Field(default=None, description="合作人物档案URL")
    collaborator_name: str | None = Field(default=None, description="合作人物")
    collaborator_homepage_url: str | None = Field(
        default=None, description="合作明星主页URL"
    )
    collaborator_profession: str | None = Field(
        default=None, description="合作人物职业"
    )
    collaboration_count: int | None = Field(default=None, description="合作作品数量")
    collaboration_works: List[str] = Field(default=[], description="合作作品列表")
    collaboration_works_homepage_url: List[str] = Field(
        default=[], description="合作作品主页URL"
    )
    collaborator_douban_followers: int | None = Field(
        default=None, description="合作人物豆瓣关注人数"
    )


class CollaborationInfo(CollaborationInfoCreate):
    id: int

    class config:
        from_attributes = True


class DoubanWorkCreate(BaseModel):
    douban_person_id: str
    douban_url: str | None = Field(None, description="豆瓣URL")
    star_work_url: Optional[str] = Field(None, description="明星作品页URL")
    work_type: Optional[str] = Field(None, description="作品类型")
    work_name: Optional[str] = Field(None, description="作品名称")
    work_url: Optional[str] = Field(None, description="作品主页URL")
    year: Optional[str] = Field(None, description="年份")
    status: Optional[str] = Field(None, description="状态")
    role: Optional[str] = Field(None, description="担任")
    director: Optional[str] = Field(None, description="导演")
    actors: Optional[str] = Field(None, description="主演")
    author: Optional[str] = Field(None, description="作者")
    publisher: Optional[str] = Field(None, description="出版社")
    performer: Optional[str] = Field(None, description="表演者")
    rating: Optional[str] = Field(None, description="评分")
    rating_count: Optional[str] = Field(None, description="评价人数")


class DoubanWork(DoubanWorkCreate):
    id: int

    class config:
        from_attributes = True


class MovieCreate(BaseModel):
    title: Optional[str] = Field(default=None, description="作品名称")
    subject_url: Optional[str] = Field(default=None, description="作品页URL")
    year: Optional[str] = Field(default=None, description="年份")
    director: Optional[str] = Field(default=None, description="导演")
    director_url: Optional[str] = Field(default=None, description="导演-明星主页URL")
    screenwriter: List[str] | None = Field(default=None, description="编剧")
    screenwriter_url: List[str] | None = Field(
        default=None, description="编剧-明星主页URL"
    )
    starring: List[str] | None = Field(default=None, description="主演")
    starring_url: Optional[List[str]] = Field(
        default=None, description="主演-明星主页URL"
    )
    genre: Optional[List[str]] = Field(default=None, description="类型")
    country: Optional[str] = Field(default=None, description="制片国家/地区")
    language: Optional[str] = Field(default=None, description="语言")
    release_date: List[str] | None = Field(
        default=None, description="上映日期（电影）/首播（真人秀/电视剧）"
    )
    runtime: Optional[str] = Field(default=None, description="片长")
    episodes: Optional[str] = Field(default=None, description="集数")
    episode_runtime: Optional[str] = Field(default=None, description="单集片长")
    aka: Optional[str] = Field(default=None, description="又名")
    imdb: Optional[str] = Field(default=None, description="IMDb")
    synopsis: Optional[str] = Field(default=None, description="简介")
    cast_count: Optional[str] = Field(default=None, description="演职人员个数")
    cast_details_url: Optional[str] = Field(
        default=None, description="作品演职员详情URL"
    )
    awards_url: Optional[str] = Field(default=None, description="作品获奖情况URL")
    douban_rating: Optional[str] = Field(default=None, description="豆瓣评分")
    rating_count: Optional[str] = Field(default=None, description="评价人数")
    watching_count: Optional[str] = Field(default=None, description="在看人数")
    watched_count: Optional[str] = Field(default=None, description="看过人数")
    want_to_watch_count: Optional[str] = Field(default=None, description="想看人数")
    five_star_ratio: Optional[str] = Field(default=None, description="5星占比")
    four_star_ratio: Optional[str] = Field(default=None, description="4星占比")
    three_star_ratio: Optional[str] = Field(default=None, description="3星占比")
    two_star_ratio: Optional[str] = Field(default=None, description="2星占比")
    one_star_ratio: Optional[str] = Field(default=None, description="1星占比")
    short_comment_count: Optional[str] = Field(default=None, description="短评条数")
    short_comment_url: Optional[str] = Field(default=None, description="短评列表URL")
    review_count: Optional[str] = Field(default=None, description="影评/剧评条数")
    review_url: Optional[str] = Field(default=None, description="影评/剧评列表URL")
    discussion_count: Optional[str] = Field(
        default=None, description="讨论区/小组讨论条数"
    )
    discussion_url: Optional[str] = Field(
        default=None, description="讨论区/小组讨论列表URL"
    )
    question_count: Optional[str] = Field(default=None, description="问题个数")
    question_url: Optional[str] = Field(default=None, description="问题列表URL")


class Movie(MovieCreate):
    id: int

    class config:
        from_attributes = True


class BookCreate(BaseModel):
    title: Optional[str] = Field(default=None, description="作品名称")
    subject_url: Optional[str] = Field(default=None, description="作品页URL")
    author: Optional[list[str]] = Field(default=None, description="作者")
    author_url: Optional[list[str]] = Field(
        default=None, description="作者-明星主页URL"
    )
    publisher: Optional[str] = Field(default=None, description="出版社")
    publisher_url: Optional[str] = Field(default=None, description="出版社主页URL")
    producer: Optional[str] = Field(default=None, description="出品方")
    producer_url: Optional[str] = Field(default=None, description="出品方主页URL")
    original_title: Optional[str] = Field(default=None, description="原作名")
    translator: Optional[str] = Field(default=None, description="译者")
    translator_url: Optional[str] = Field(default=None, description="译者主页URL")
    publication_year: Optional[str] = Field(default=None, description="出版年")
    pages: Optional[str] = Field(default=None, description="页数")
    binding: Optional[str] = Field(default=None, description="装帧")
    series: Optional[str] = Field(default=None, description="丛书")
    series_url: Optional[str] = Field(default=None, description="丛书主页URL")
    isbn: Optional[str] = Field(default=None, description="ISBN")
    synopsis: Optional[str] = Field(default=None, description="内容简介")
    author_intro: Optional[str] = Field(default=None, description="作者简介")
    table_of_contents: Optional[str] = Field(default=None, description="目录")
    series_info: Optional[str] = Field(default=None, description="丛书信息")
    douban_rating: Optional[str] = Field(default=None, description="豆瓣评分")
    rating_count: Optional[str] = Field(default=None, description="评价人数")
    reading_count: Optional[str] = Field(default=None, description="在读人数")
    read_count: Optional[str] = Field(default=None, description="读过人数")
    want_to_read_count: Optional[str] = Field(default=None, description="想读人数")
    five_star_ratio: Optional[str] = Field(default=None, description="5星占比")
    four_star_ratio: Optional[str] = Field(default=None, description="4星占比")
    three_star_ratio: Optional[str] = Field(default=None, description="3星占比")
    two_star_ratio: Optional[str] = Field(default=None, description="2星占比")
    one_star_ratio: Optional[str] = Field(default=None, description="1星占比")
    short_comment_count: Optional[str] = Field(default=None, description="短评条数")
    short_comment_url: Optional[str] = Field(default=None, description="短评列表URL")
    review_count: Optional[str] = Field(default=None, description="书评条数")
    review_url: Optional[str] = Field(default=None, description="书评列表URL")
    reading_note_count: Optional[str] = Field(default=None, description="读书笔记条数")
    reading_note_url: Optional[str] = Field(default=None, description="读书笔记列表URL")


class Book(BookCreate):
    id: int

    class config:
        from_attributes = True


class MusicCreate(BaseModel):
    title: str | None = Field(default=None, description="作品名称")
    subject_url: str | None = Field(default=None, description="作品页URL")
    aka: str | None = Field(default=None, description="又名")
    performer: list[str] | None = Field(default=None, description="表演者")
    performer_url: list[str] | None = Field(
        default=None, description="表演者-明星主页URL"
    )
    genre: str | None = Field(default=None, description="流派")
    album_type: str | None = Field(default=None, description="专辑类型")
    medium: str | None = Field(default=None, description="介质")
    release_date: str | None = Field(default=None, description="发行时间")
    publisher: str | None = Field(default=None, description="出版者")
    disc_count: str | None = Field(default=None, description="唱片数")
    barcode: str | None = Field(default=None, description="条形码")
    related_movie: str | None = Field(default=None, description="相关电影")
    related_movie_url: str | None = Field(
        default=None, description="相关电影-作品主页URL"
    )
    synopsis: str | None = Field(default=None, description="简介")
    track_list: list[str] | None = Field(default=None, description="曲目")
    douban_rating: str | None = Field(default=None, description="豆瓣评分")
    rating_count: str | None = Field(default=None, description="评价人数")
    listening_count: str | None = Field(default=None, description="在听人数")
    listened_count: str | None = Field(default=None, description="听过人数")
    want_to_listen_count: str | None = Field(default=None, description="想听人数")
    five_star_ratio: str | None = Field(default=None, description="5星占比")
    four_star_ratio: str | None = Field(default=None, description="4星占比")
    three_star_ratio: str | None = Field(default=None, description="3星占比")
    two_star_ratio: str | None = Field(default=None, description="2星占比")
    one_star_ratio: str | None = Field(default=None, description="1星占比")
    short_comment_count: str | None = Field(default=None, description="短评条数")
    short_comment_url: str | None = Field(default=None, description="短评列表URL")
    review_count: str | None = Field(default=None, description="乐评条数")
    review_url: str | None = Field(default=None, description="乐评列表URL")


class Muscic(MusicCreate):
    id: int

    class config:
        from_attributes = True


class SubjectAwardCreate(BaseModel):
    title: str | None = Field(default=None, description="作品名称")
    award_url: str | None = Field(default=None, description="作品获奖情况URL")
    year: str | None = Field(default=None, description="年份")
    award_name: str | None = Field(default=None, description="奖名")
    award_name_url: str | None = Field(default=None, description="奖名URL")
    specific_award: str | None = Field(default=None, description="具体奖项")
    winner: str | None = Field(default=None, description="获奖人")
    winner_url: str | None = Field(default=None, description="获奖人-明星主页URL")


class SubjectAward(SubjectAwardCreate):
    id: int

    class config:
        from_attributes = True


class CastCreate(BaseModel):
    douban_subject_id: str | None = Field(default=None, description="作品ID")
    title: str | None = Field(default=None, description="作品名称")
    cast_list_url: str | None = Field(default=None, description="作品演职员列表URL")
    role_category: str | None = Field(default=None, description="职位类别")
    cast_name: str | None = Field(default=None, description="演职员姓名")
    cast_url: str | None = Field(default=None, description="演职员-明星主页URL")
    order: str | None = Field(default=None, description="顺序排位")
    specific_role: str | None = Field(default=None, description="具体职位")
    representative_work: str | None = Field(default=None, description="代表作")
    representative_work_url: str | None = Field(
        default=None, description="代表作-作品主页URL"
    )


class Cast(CastCreate):
    id: int

    class config:
        from_attributes = True
