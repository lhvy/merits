import csv
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from progress.bar import Bar

from filters import fetch_url, get_badge_filter, get_dates, get_year, get_year_filter
from model import Achievements, ProcessedStudent, Student, Users

load_dotenv()

AUTH = os.getenv("AUTH")
HOST = os.getenv("HOST")

if not AUTH or not HOST or not os.getenv("TRACKED_BADGES"):
    raise ValueError("Missing environment variables")


USERS_URL = HOST + "/api/user"
ACHIEVEMENTS_URL = HOST + "/learning/evidenceFeed/user"
headers = {
    "Authorization": AUTH,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

TRACKED_BADGES = os.getenv("TRACKED_BADGES").split(",")


def main():
    year = get_year()
    start_date, end_date = get_dates()

    students = get_students(year)
    processed = get_processed(start_date, end_date, students)

    # for student in processed:
    #     print(student.fullName, student.externalId)
    #     for badge in student.badges:
    #         print(f"  {badge.name}: {badge.count}")

    write_out(year, processed)


def get_students(year):
    user_filter = get_year_filter(year)
    cursor = None
    progress_bar = None
    students: list[Student] = []
    while True:
        res = fetch_url(f"{USERS_URL}?filter={user_filter}&cursor={cursor}", headers)
        if res.status_code != 200:
            print(f"Failed to get users: {res.text}")
            sys.exit(1)
        users = Users.model_validate_json(res.text)
        cursor = users.metadata.cursor
        students += users.data
        if not progress_bar:
            progress_bar = Bar("Fetching students", max=users.metadata.count)
        progress_bar.next(len(users.data))
        if len(students) >= users.metadata.count:
            break
    progress_bar.finish()
    return students


def get_processed(start_date, end_date, students):
    processed: list[ProcessedStudent] = []
    progress_bar = Bar("Fetching badges", max=len(students))
    for student in students:
        p = ProcessedStudent(
            schoolboxId=student.id,
            externalId=(
                int(student.externalId) if student.externalId is not None else -1
            ),
            fullName=student.fullName,
            firstName=student.firstName,
            lastName=student.lastName,
            badges={},
        )

        achievements_filter = get_badge_filter()
        cursor = None
        seen = 0
        while True:
            url = f"{ACHIEVEMENTS_URL}/{student.id}?filter={achievements_filter}"
            if cursor:
                url += f"&cursor={cursor}"
            res = fetch_url(url, headers=headers)
            if res.status_code != 200:
                print(f"Failed to get achievements: {res.text}")
                sys.exit(1)
            achievements = Achievements.model_validate_json(res.text)

            for achievement in achievements.data:
                seen += 1

                # ensure the badge is between the start and end date
                # achievement.date is RFC3339 format, i.e. "2024-07-30T11:07:35+10:00"
                badge_date = datetime.strptime(achievement.date, "%Y-%m-%dT%H:%M:%S%z")
                if badge_date < start_date or badge_date >= end_date:
                    continue

                badge = achievement.object.badge.name
                p.add_badge(badge)

            if (
                seen == achievements.metadata.count
                or not achievements.metadata.cursor.next
            ):
                break
            cursor = achievements.metadata.cursor.next

        progress_bar.next()
        processed.append(p)
    progress_bar.finish()
    return processed


def write_out(year, processed):
    with open(f"{year}-output.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        header = [
            "External ID",
            "First Name",
            "Last Name",
        ] + TRACKED_BADGES
        writer.writerow(header)
        for student in processed:
            row = [
                student.externalId,
                student.firstName,
                student.lastName,
            ]
            for badge in TRACKED_BADGES:
                row.append(student.get_badge(badge))
            writer.writerow(row)


if __name__ == "__main__":
    main()
