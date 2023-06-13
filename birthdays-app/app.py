# Description: A simple app that counts down days to birthday

# Import libraries
from shiny import *
from pathlib import Path
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Import the data
file_path = Path(__file__).parent / "birthdates.csv"
## Read the data file using pandas
data = pd.read_csv(file_path)

## Alternatively, you can import a public CSV file from a URL such as the one below
# public_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSiiCJ2cx7WYplflvzmZOWwfI8zhGYJ109sLGpCMD9yWyKxK6fFZ_e7UOPkWq8LbxjGJlTfCAjCwYSx/pub?gid=0&single=true&output=csv"
# data = pd.read_csv(public_url)


# Define helper functions
def day_difference(start_date, end_date):
    time_remaining = end_date - start_date
    return time_remaining.days


def calculate_age(birthday_date):
    today = datetime.today()
    age = (
        today.year
        - birthday_date.year
        - ((today.month, today.day) < (birthday_date.month, birthday_date.day))
    )
    return age


def custom_message(days, person_name, birthday_date):
    fmt_bday = format_date(birthday_date)
    message = f"There are {days} days remaining until {person_name}'s birthday."
    message += " " + f"{person_name} was born on {fmt_bday}"
    message += " " + f"and will be {calculate_age(birthday_date)} years old this year."
    if days == 0:
        message = f"Happy birthday to {person_name}!" + " " + message
    if days < 0:
        message = f"Happy belated birthday to {person_name}!" + " " + message
    return message


def format_date(dob):
    return dob.strftime("%B %d, %Y")


# Create a list of choices
choices = list(data["name"])

# Create the app UI
app_ui = ui.page_fluid(
    # shinyswatch.theme.minty(),
    ui.h1("Birthday countdown app"),
    ui.navset_tab_card(
        ui.nav(
            "List upcoming",
            ui.input_slider(
                "count", "List a number of upcoming birthdays:", min=1, max=20, value=5
            ),
            ui.output_text_verbatim("count_remaining"),
        ),
        ui.nav(
            "Search person",
            ui.input_selectize("name", "Search a person", choices, selected=None),
            ui.input_action_button("submit", "Search"),
            ui.tags.br(),
            ui.tags.br(),
            ui.output_text("days_remaining"),
        ),
    ),
)


# Create the app server
def server(input, output, session):
    @output
    @render.text
    @reactive.event(input.submit, ignore_none=False)
    def days_remaining():
        # calculate time from now to next birthday
        today = datetime.today()
        dob = data[data["name"] == input.name()]["date"].values[0]
        dob = datetime.strptime(dob, "%Y-%m-%d")
        # change year to current year
        birthday = dob.replace(year=today.year)
        days_remaining = day_difference(today, birthday)
        # return the time remaining in months and days
        return custom_message(days_remaining, input.name(), dob)

    @output
    @render.text
    def count_remaining():
        num_people = input.count()
        # create a list of tuples containing the name and date of birth for each person
        people = []
        for index, row in data.iterrows():
            name = row["name"]
            dob = datetime.strptime(row["date"], "%Y-%m-%d")
            people.append((name, dob))

        # calculate the time from now to each person's next birthday
        today = datetime.today()
        results = []
        for name, dob in people:
            # change year to current year
            birthday = dob.replace(year=today.year)
            days_remaining = day_difference(today, birthday)
            age = calculate_age(dob)
            if days_remaining < -1:
                birthday = dob.replace(year=today.year + 1)
                days_remaining = day_difference(today, birthday)
                age = age + 1
            results.append((name, dob, days_remaining, age))

        # sort the results by the number of days remaining
        results.sort(key=lambda x: x[2])
        # filter the results to only include the number of people specified by the user
        results = results[:num_people]

        # return a list of tuples containing the name and date of birth for each person,
        # along with the number of days remaining until their next birthday
        def format_results(results):
            lines = []
            for name, dob, days, age in results:
                line = f"{name} will be {age} years old in {days} days ({format_date(dob)})."
                lines.append(line)
            return "\n".join(lines)

        return format_results(results)


# Create the app
app = App(app_ui, server)
