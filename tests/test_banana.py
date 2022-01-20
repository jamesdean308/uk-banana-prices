import pytest

import datetime as dt
import pandas as pd

import src.banana


@pytest.mark.parametrize(
    "date_,day_name,expected",
    [
        (dt.date(2022, 1, 13), "monday", dt.date(2022, 1, 10)),
        (dt.date(2022, 1, 13), "tuesday", dt.date(2022, 1, 11)),
        (dt.date(2022, 1, 13), "wednesday", dt.date(2022, 1, 12)),
        (dt.date(2022, 1, 13), "thursday", dt.date(2022, 1, 6)),
        (dt.date(2022, 1, 13), "friday", dt.date(2022, 1, 7)),
        (dt.date(2022, 1, 13), "saturday", dt.date(2022, 1, 8)),
        (dt.date(2022, 1, 13), "sunday", dt.date(2022, 1, 9)),
        (dt.date(2022, 1, 10), "monday", dt.date(2022, 1, 3)),
    ],
)
def test_get_last_weekday_date_successful(date_, day_name, expected):
    assert src.banana.get_last_weekday_date(date_, day_name) == expected


@pytest.mark.parametrize(
    "date_,day_name",
    [
        (dt.date(2022, 1, 13), "montag"),
        (dt.date(2022, 1, 13), "toosday"),
        (dt.date(2022, 1, 13), "wed"),
        (dt.date(2022, 1, 13), "thersday"),
        (dt.date(2022, 1, 13), "fritag"),
        (dt.date(2022, 1, 13), "samedi"),
        (dt.date(2022, 1, 13), "sun day"),
    ],
)
def test_get_last_weekday_date_value_error(date_, day_name):
    with pytest.raises(ValueError):
        src.banana.get_last_weekday_date(date_, day_name)


@pytest.mark.parametrize(
    "date_,expected",
    [
        (dt.date(2022, 1, 13), "bananas-13jan22.csv"),
        (dt.date(2022, 1, 1), "bananas-1jan22.csv"),
    ],
)
def test_get_file_name_successful(date_, expected):
    assert src.banana.get_file_name(date_) == expected
