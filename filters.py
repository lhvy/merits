import base64
import sys
import time
import urllib.parse

import requests


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
