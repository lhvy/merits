from dataclasses import dataclass

from pydantic import BaseModel


class Cursor(BaseModel):
    current: str | None
    next: str | None


class Metadata(BaseModel):
    count: int
    cursor: int | Cursor


class YearLevel(BaseModel):
    id: int
    name: str


class Student(BaseModel):
    id: int
    yearLevel: YearLevel
    isDeleted: bool
    fullName: str
    externalId: str
    username: str
    enabled: bool
    title: str
    firstName: str
    lastName: str
    preferredName: str | None


class Users(BaseModel):
    data: list[Student]
    metadata: Metadata


class Badge(BaseModel):
    id: int
    name: str


class AchievementBadge(BaseModel):
    id: int
    badge: Badge


class Achievement(BaseModel):
    discriminator: str
    object: AchievementBadge
    date: str  # The date as a RFC3339 string


class Achievements(BaseModel):
    data: list[Achievement]
    metadata: Metadata


@dataclass
class ProcessedStudent:
    schoolboxId: int
    externalId: int
    fullName: str
    firstName: str
    lastName: str
    badges: dict[str, int]

    def add_badge(self, name: str, count: int = 1) -> None:
        badge = self.badges.get(name, 0)
        self.badges[name] = badge + count

    def get_badge(self, name: str) -> int:
        return self.badges.get(name, 0)
