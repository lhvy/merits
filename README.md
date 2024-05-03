# Merits

[Schoolbox](https://schoolbox.education/) does not support fetching achievements from their API intended for end-users. This inconvenience can be bypassed by using the JSON data that is served to web browsers when viewing achievements for a class/student.

This project can pull achievement data from the correct URL (see .env.example) and parse it, as well as fetching more detailed information about each recipient of an achievement, finally outputting all data into CSV format.

## Usage

1. Ensure Python 3 is installed (tested on 3.12)
2. Install dependencies with `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in the required fields
4. Run the script with `python main.py`
5. Output will be displayed in the console and saved to `output.csv`
