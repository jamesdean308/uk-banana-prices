from datetime import date, datetime, timedelta
import logging
import os
import pandas as pd
import urllib


def get_last_weekday_date(date_: date, day_name: str = "monday") -> date:
    """Given a date and day of the week, return datetime of the most recent occurance of said day of week before given date.
    Will return date_ -7 days if day of week is on that date.

    Args:
        date_ (date): Any date.
        day_name (str, optional): One of seven days of the week eg 'monday'. Defaults to "monday".

    Returns:
        date: Most recent occurance of said day of week before given date.
    """
    days_of_week = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    target_day = days_of_week.index(day_name.lower())
    delta_day = target_day - date_.isoweekday()
    if delta_day >= 0:
        delta_day -= 7  # go back 7 days
    return date_ + timedelta(days=delta_day)


def get_file_name(date_: date) -> str:
    """Transform date into formatted government banana file string.

    Args:
        date_ (date): Any date.

    Returns:
        str: Formatted government banana file string.
    """

    # NOTE there is not a clean way to do this with a single strftime due to the nature of the gov's file name format.
    day_of_month = date_.day
    month_ = date_.strftime("%b").lower()
    year_ = date_.strftime("%y")

    return f"bananas-{day_of_month}{month_}{year_}.csv"


def get_banana_df(
    banana_file_url_root: str, most_recent_banana_file: str, local_banana_file_path: str
) -> pd.DataFrame:
    """Attempt to get banana file from GOV website. If that fails read the local backup file.

    NOTE this function is a bit of a pain to unit test in its current form.
    Could be tested using mocking, but would require modify the source code and compromising its readability.
    Consider a different approuch.

    Args:
        banana_file_url_root (str): GOV banana file url root including trailing /.
        most_recent_banana_file (str): File name of most recent banana csv file.
        local_banana_file_path (str): Path to local backup banana file.

    Returns:
        pd.DataFrame: UK banana prices data.
    """
    try:
        logging.info("Attempting to get file from GOV website...")
        df = pd.read_csv(
            banana_file_url_root + most_recent_banana_file,
            encoding="unicode_escape",
            parse_dates=["Date"],
            date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y"),
        )
        logging.info(
            f"Successfully loaded: {banana_file_url_root + most_recent_banana_file}"
        )

    # If we fail to get file from gov website, load local instead.
    except urllib.error.HTTPError:
        logging.warning(
            f"Failed to get file at: {banana_file_url_root + most_recent_banana_file}\nAttempting to get local file..."
        )
        df = pd.read_csv(
            local_banana_file_path,
            encoding="unicode_escape",
            parse_dates=["Date"],
            date_parser=lambda x: datetime.strptime(x, "%d/%m/%Y"),
        )
        logging.info(
            f"Successfully loaded: {os.path.dirname(os.path.realpath(__file__))}\\{local_banana_file_path}"
        )

    return df
