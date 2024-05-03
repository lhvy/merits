import csv
import os

from dotenv import load_dotenv

from processed import process_students
from raw import get_raw

load_dotenv()
cookies = {"PHPSESSID": os.getenv("PHPSESSID")}
raw = get_raw(os.getenv("ACHIEVEMENTS_URL"), cookies)
processed = process_students(raw.data, os.getenv("BASE_URL"), cookies)
for student in processed:
    print(student.fullName, student.externalId)
    for badge in student.badges:
        print(f"  {badge.name}: {badge.count}")

with open("output.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            "External ID",
            "First Name",
            "Last Name",
            "Badge Name",
            "Count",
        ]
    )
    for student in processed:
        for badge in student.badges:
            writer.writerow(
                [
                    student.externalId,
                    student.firstName,
                    student.lastName,
                    badge.name,
                    badge.count,
                ]
            )
