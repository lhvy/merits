import csv
import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv
from progress.bar import Bar
from pytz import timezone

from filters import fetch_url, get_badge_filter, get_year_filter
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

students: list[Student] = []

year = input("Enter year level (7-13): ")
if year not in ["7", "8", "9", "10", "11", "12", "13"]:
    print("Invalid year level")
    sys.exit(1)

valid = False
while not valid:
    start_date = input("Enter start date (inclusive) in format YYYY-MM-DD: ")
    end_date = input("Enter end date (inclusive) in format YYYY-MM-DD: ")
    try:
        tz = timezone("Australia/Sydney")
        start_date = tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
        end_date = tz.localize(datetime.strptime(end_date, "%Y-%m-%d")) + timedelta(
            days=1
        )
        if start_date < end_date:
            valid = True
        else:
            print("Start date must be before end date")
    except ValueError:
        print("Invalid date format")

user_filter = get_year_filter(year)
cursor = None
progress_bar = None
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

processed: list[ProcessedStudent] = []
progress_bar = Bar("Fetching badges", max=len(students))
for student in students:
    p = ProcessedStudent(
        schoolboxId=student.id,
        externalId=int(student.externalId),
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

        if seen == achievements.metadata.count or not achievements.metadata.cursor.next:
            break
        cursor = achievements.metadata.cursor.next

    progress_bar.next()
    processed.append(p)
progress_bar.finish()

# for student in processed:
#     print(student.fullName, student.externalId)
#     for badge in student.badges:
#         print(f"  {badge.name}: {badge.count}")

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
