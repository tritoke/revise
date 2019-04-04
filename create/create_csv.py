#!/usr/bin/env python
from csv import writer
from json import loads
from random import sample
import numpy as np
import pandas as pd
import re

# read in settings from json file
settings = loads(open("config.json").read())


def htm(hourstring: str) -> int:
    """
    Takes in a string in hours:minutes form e.g. 12:00
    and returns it as just minutes.
    """
    if re.match(r"\d\d?:\d\d?", hourstring):
        hours, mins = map(int, hourstring.split(":"))
        return (60 * hours) + mins
    else:
        raise ValueError(
            f"input {hourstring} not in hours:minutes form."
        )


def mth(minutes: int) -> str:
    """
    the reverse of htm: takes in a number of minutes
    and turns that into hours:minute form
    """
    return ":".join(f"{i:>02d}" for i in divmod(minutes, 60))


# structure the morning

total_morning_time = (
    htm(settings["lunch_start_time"])
    - htm(settings["earliest_start_time"])
)

desired_morning_session_time = (
    settings["best_session_length"]
    * settings["morning_sessions"]
)

morning_breaks = settings["morning_sessions"] - 1

morning_break_time = morning_breaks * settings["break_between_sessions"]

morning_working_time = morning_break_time + desired_morning_session_time

morning_difference = (
    total_morning_time - morning_working_time
)

if morning_difference > 0:
    # base case: everything works and there is
    # extra time after the earliest_start_time
    morning_start_time = (
        htm(settings["earliest_start_time"])
        + morning_difference
    )
    morning_session_length = settings["best_session_length"]
    morning_break_length = settings["break_between_sessions"]

elif morning_difference == 0:
    # case that there is *just* enough time
    morning_start_time = htm(settings["earliest_start_time"])
    morning_session_length = settings["best_session_length"]
    morning_break_length = settings["break_between_sessions"]

else:
    # case that there is enough time when breaks aren't included
    # therefore shorten the breaks to fit to a minimum of 10 mins
    morning_start_time = htm(settings["earliest_start_time"])

    available_break_time = total_morning_time - desired_morning_session_time
    if available_break_time // morning_breaks >= 10:
        # case that there is enough time for ten minute or longer breaks
        morning_session_length = settings["best_session_length"]
        morning_break_length = available_break_time // morning_breaks
    else:
        # case that there isn't even enough time for 10 minute breaks
        # therefore shorten the work period
        available_work_time = total_morning_time - (morning_breaks * 10)

        morning_session_length = (
            available_work_time // settings["morning_sessions"]
        )
        morning_break_length = 10

# structure the afternoon
total_afternoon_time = (
    htm(settings["latest_finish_time"])
    - htm(settings["lunch_end_time"])
)

desired_afternoon_session_time = (
    settings["best_session_length"]
    * settings["afternoon_sessions"]
)

afternoon_breaks = settings["afternoon_sessions"] - 1

afternoon_break_time = afternoon_breaks * settings["break_between_sessions"]

afternoon_working_time = afternoon_break_time + desired_afternoon_session_time

afternoon_difference = (
    total_afternoon_time - afternoon_working_time
)

if afternoon_difference > 0:
    # base case: everything works and there is
    # extra time to finish early
    afternoon_end_time = (
        htm(settings["latest_finish_time"])
        - afternoon_difference
    )
    afternoon_session_length = settings["best_session_length"]
    afternoon_break_length = settings["break_between_sessions"]

elif afternoon_difference == 0:
    # case that there is *just* enough time
    afternoon_end_time = htm(settings["latest_finish_time"])
    afternoon_session_length = settings["best_session_length"]
    afternoon_break_length = settings["break_between_sessions"]

else:
    # case that there is enough time when breaks aren't included
    # therefore shorten the breaks to fit to a minimum of 10 mins
    afternoon_end_time = htm(settings["latest_finish_time"])

    available_break_time = (
        total_afternoon_time - desired_afternoon_session_time
    )
    if available_break_time // afternoon_breaks >= 10:
        # case that there is enough time for ten minute or longer breaks
        afternoon_session_length = settings["best_session_length"]
        afternoon_break_length = available_break_time // afternoon_breaks
    else:
        # case that there isn't even enough time for 10 minute breaks
        # therefore shorten the work period
        available_work_time = total_afternoon_time - (afternoon_breaks * 10)

        afternoon_session_length = (
            available_work_time // settings["afternoon_sessions"]
        )
        afternoon_break_length = 10

# assign the sessions

# create the list of dates
if settings["only_weekdays"]:
    dates = pd.bdate_range(
        start=settings["start"],
        end=settings["end"]
    )
else:
    dates = pd.date_range(
        start=settings["start"],
        end=settings["end"]
    )

# format the dates
date_strings = [str(date).split()[0] for date in dates]

days = len(date_strings)

# - 1 because free session each day
sessions_per_day = (
    settings["morning_sessions"] + settings["afternoon_sessions"] - 1
)

num_sessions = days * sessions_per_day

num_cycles, remainder = divmod(num_sessions, len(settings["subjects"]))

sessions = (
    num_cycles * settings["subjects"]
    + sample(settings["subjects"], k=remainder)
)

data = np.array(sessions).reshape((sessions_per_day, days))

np.random.shuffle(data.flat)

data = np.array([
    np.array(
        sample(
            (*i, settings["free_time_activity"]),
            k=(sessions_per_day + 1)
        )
    )
    for i in data.transpose()
]).transpose()

data = np.array([date_strings, *data])

# generate column labels

morning_labels = [
    mth(
        morning_start_time
        + i * (morning_session_length + morning_break_length)
    ) + "-"
    + mth(
        morning_start_time
        + morning_session_length
        + (morning_session_length + morning_break_length) * i
    )
    for i in range(settings["morning_sessions"])
]

afternoon_labels = [
    mth(
        htm(settings["lunch_end_time"])
        + i * (afternoon_session_length + afternoon_break_length)
    ) + "-"
    + mth(
        htm(settings["lunch_end_time"])
        + afternoon_session_length
        + (afternoon_session_length + afternoon_break_length) * i
    )
    for i in range(settings["afternoon_sessions"])
]

labels = ("Date", *morning_labels, *afternoon_labels)

data = np.array([
    np.array([
        labels[i], *j
    ])
    for i, j in enumerate(data)
]).transpose()

with open("revision.csv", "w") as csvfile:
    revision_writer = writer(csvfile)
    revision_writer.writerows(data)

