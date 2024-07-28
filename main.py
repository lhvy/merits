import csv
import os

from dotenv import load_dotenv

from filters import ask_user_filters, get_filters
from processed import Student, process_students
from raw import get_raw

load_dotenv()
PHPSESSID = os.getenv("PHPSESSID")
BASE_URL = os.getenv("BASE_URL")

if (
    not PHPSESSID
    or not BASE_URL
    or not os.getenv("CLASSES")
    or not os.getenv("TRACKED_BADGES")
):
    raise ValueError("Missing environment variables")

ACHIEVEMENTS_URL = BASE_URL + "/learning/badge/award/list"

TRACKED_BADGES = os.getenv("TRACKED_BADGES").split(",")

CLASSES = os.getenv("CLASSES").split(",")
for c in CLASSES:
    if not c.isdigit():
        raise ValueError(f"Invalid class: {c}")

COOKIES = {"PHPSESSID": PHPSESSID}

FILTERS_URL = ACHIEVEMENTS_URL + "/" + CLASSES[0]
raw_filters = get_filters(FILTERS_URL, COOKIES)
filters = ask_user_filters(raw_filters)

processed: list[Student] = []
for c in CLASSES:
    if raw_filters != get_filters(ACHIEVEMENTS_URL + "/" + c, COOKIES):
        raise ValueError("Filters have changed")

    raw = get_raw(ACHIEVEMENTS_URL + "/" + c + "/data?" + filters, COOKIES)
    processed += process_students(raw.data, c, BASE_URL, COOKIES)

# for student in processed:
#     print(student.fullName, student.externalId)
#     for badge in student.badges:
#         print(f"  {badge.name}: {badge.count}")

with open("output.csv", "w", newline="", encoding="utf-8") as file:
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
