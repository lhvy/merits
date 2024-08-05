# Merits

Pulls achievement data (otherwise known as badges/awards) from [Schoolbox](https://schoolbox.education/), and generates reports of student badges within a given year group and time-frame.

## Usage

1. Ensure Python 3 is installed (tested on 3.12)
2. Install dependencies with `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in the required fields
4. Run the script with `python main.py`
5. Output will be displayed in the console and saved to `<year>-output.csv`

### Notes

- Ensure the year name is 100% accurate, in my case, this was just `7`, `8`, `9`, etc.
- The badge names in the `.env` are capital and whitespace sensitive, ensure they are the full name exactly as written in Schoolbox, separated by `,`
- If you are getting frequent timeouts/exceptions, try tweaking the parameters of `fetch_url` in `filters.py`
