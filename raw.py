from dataclasses import dataclass
from pydantic import BaseModel

import requests


@dataclass
class RawBadge(BaseModel):
    id: int
    name: str
    # createdAt: str
    # createdBy: any
    # updatedAt: str
    # updatedBy: any
    # body: str
    # image: any
    # icon: str | None
    # allowAsGoal: bool
    # animate: bool
    # category: any
    # achievementExpiry: str | None
    # goalExpiry: str | None
    # curriculumNotes: list[str]
    # tags: any
    # _links: any


@dataclass
class RawAchievement(BaseModel):
    id: int
    badge: RawBadge
    status: str
    count: int
    # reason: str
    # isGoal: bool
    # award: any
    # recipient: any
    # awardedBy: any
    # awardedAt: str
    # reasonedBy: any
    # reasonedAt: str
    # expiresAt: str | None
    # viewedOn: str | None
    # _links: any


@dataclass
class RawStudent(BaseModel):
    id: int
    fullName: str
    firstName: str
    lastName: str
    role: str
    badges: dict[str, RawAchievement] | None


@dataclass
class RawResponse(BaseModel):
    data: list[RawStudent]


def get_raw(url: str, cookies: dict[str, str]) -> RawResponse:
    response = requests.get(url, cookies=cookies, timeout=5)
    response.raise_for_status()
    return RawResponse.model_validate(response.json())
