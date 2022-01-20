from bs4 import BeautifulSoup
import datetime as dt
import logging
import os
import pandas as pd
import re
import requests
import urllib

# NOTE holding onto this function. Could be of use in the future.
# def get_last_weekday_date(date_: dt.date, day_name: str = "monday") -> dt.date:
#     """Given a date and day of the week, return datetime of the most recent occurance of said day of week before given date.
#     Will return date_ -7 days if day of week is on that date.

#     Args:
#         date_ (dt.date): Any date.
#         day_name (str, optional): One of seven days of the week eg 'monday'. Defaults to "monday".

#     Returns:
#         dt.date: Most recent occurance of said day of week before given date.
#     """
#     days_of_week = [
#         "sunday",
#         "monday",
#         "tuesday",
#         "wednesday",
#         "thursday",
#         "friday",
#         "saturday",
#     ]
#     target_day = days_of_week.index(day_name.lower())
#     delta_day = target_day - date_.isoweekday()
#     if delta_day >= 0:
#         delta_day -= 7  # go back 7 days
#     return date_ + dt.timedelta(days=delta_day)

# def get_file_name(date_: dt.date) -> str:
#     """Transform date into formatted government banana file string.
#     Args:
#         date_ (dt.date): Any date.
#     Returns:
#         str: Formatted government banana file string.
#     """

#     # NOTE there is not a clean way to do this with a single strftime due to the nature of the gov's file name format.
#     day_of_month = date_.day
#     month_ = date_.strftime("%b").lower()
#     year_ = date_.strftime("%y")

#     return f"bananas-{day_of_month}{month_}{year_}.csv"


def get_file_url() -> str:
    """Janky webscraper for extracting banana download url from gov website.
    There may be a better way to do this if you know bs4 better than I do.

    WARNING subject to gov html changing.

    Raises:
        ValueError: If html is not structured how expected.
        ValueError: If html is not structured how expected.

    Returns:
        str: Banana file url.
    """

    # NOTE keeping this in function since it is closely tied to this code.
    url = "https://www.gov.uk/government/statistical-data-sets/banana-prices"

    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "html.parser")

    download_span_tags = soup.findAll("span", {"class": "download"})

    if len(download_span_tags) != 1:
        raise ValueError(
            'Number of "span", {"class": "download"} in',
            url,
            f"!= 1.\nExpected 1, got {len(download_span_tags)}.",
        )

    gov_uk_link_a_tags = download_span_tags[0].findAll(
        "a",
        {
            "class": "govuk-link",
            "href": re.compile(
                r"^https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/.*.csv$"
            ),
        },
    )

    if len(gov_uk_link_a_tags) != 1:
        raise ValueError(
            'Number of "a", { "class": "govuk-link", "href": re.compile( r"^https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/.*.csv$" )} in single "span", {"class": "download"} tag in ',
            url,
            f"!= 1. \nExpected 1, got {len(gov_uk_link_a_tags)}.",
        )

    return gov_uk_link_a_tags[0]["href"]


def get_df() -> pd.DataFrame:
    """Attempt to get banana file from GOV website. If that fails read the local backup file.

    NOTE this function is a bit of a pain to unit test in its current form.
    Could be tested using mocking, but would require modify the source code and compromising its readability.
    Consider a different approuch.

    Returns:
        pd.DataFrame: UK banana prices data.
    """
    # Try get file from GOV website.
    try:
        logging.info("Attempting to get file from GOV website...")
        banana_file_url = get_file_url()
        df = pd.read_csv(
            banana_file_url,
            encoding="unicode_escape",
            parse_dates=["Date"],
            date_parser=lambda x: dt.datetime.strptime(x, "%d/%m/%Y"),
        )
        logging.info(f"Successfully loaded: {banana_file_url}")

    # If fail to get file from gov website, load local instead.
    except (urllib.error.HTTPError, ValueError):
        logging.warning(
            f"Failed to get file at: {banana_file_url}\nAttempting to get local file..."
        )

        local_banana_file_path = "data/bananas-1nov21.csv"

        df = pd.read_csv(
            local_banana_file_path,
            encoding="unicode_escape",
            parse_dates=["Date"],
            date_parser=lambda x: dt.datetime.strptime(x, "%d/%m/%Y"),
        )
        logging.info(
            f"Successfully loaded: {os.path.dirname(os.path.realpath(__file__))}\\{local_banana_file_path}"
        )

    return df
