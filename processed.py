from dataclasses import dataclass

import requests
from progress.bar import Bar

from raw import RawStudent


@dataclass
class Badge:
    id: int
    name: str
    count: int


@dataclass
class Student:
    schoolboxId: int
    externalId: int
    fullName: str
    firstName: str
    lastName: str
    badges: list[Badge]


def process_students(
    raw_students: list[RawStudent], base_url: str, cookies: dict[str, str]
) -> list[Student]:
    students = []
    ids = set()
    bar = Bar("Processing", max=len(raw_students))
    for raw_student in raw_students:
        url = f"{base_url}/api/user/{raw_student.id}"
        response = requests.get(url, cookies=cookies, timeout=5)
        response.raise_for_status()
        externalId = int(response.json().get("externalId"))

        if raw_student.badges is None:
            bar.next()
            continue

        student = Student(
            schoolboxId=raw_student.id,
            externalId=externalId,
            fullName=raw_student.fullName,
            firstName=raw_student.firstName,
            lastName=raw_student.lastName,
            badges=[
                Badge(
                    id=badge.badge.id,
                    name=badge.badge.name,
                    count=badge.count,
                )
                for badge in raw_student.badges.values()
            ],
        )
        if externalId in ids:
            raise ValueError(f"Duplicate external ID: {externalId}")
        ids.add(externalId)
        students.append(student)
        bar.next()

    bar.finish()
    return students
