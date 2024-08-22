import base64
import sys
import time
import urllib.parse
from datetime import datetime, timedelta

import requests
from pytz import timezone


def get_year():
    year = input("Enter current year level (7-13): ")
    if year not in ["7", "8", "9", "10", "11", "12", "13"]:
        print("Invalid year level")
        sys.exit(1)
    return year


def get_dates():
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
    return start_date, end_date


def get_year_filter(name: str) -> str:
    filter_data = f'{{"year": {{"name": {name}}}, "roleType": "student"}}'
    encoded_filter = urllib.parse.quote(filter_data)
    return encoded_filter


def get_badge_filter() -> str:
    filter_data = '{"filterNames": ["achievements"], "tag": ""}'
    encoded_filter = base64.b64encode(filter_data.encode()).decode()
    return encoded_filter


def fetch_url(url, headers, retries=5, backoff_factor=0.3) -> requests.Response:
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            return response
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                time.sleep(backoff_factor * (2**i))
            else:
                print(f"Failed to connect to {url}: {e}")
                sys.exit(1)

    return None
