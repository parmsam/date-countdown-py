# Description: A simple app that counts down days to event
# Import libraries
from shiny import *

# import shinyswatch
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Import the data
## Get the current working directory
cwd = os.getcwd()
## Define the file path relative to the current working directory
# file_path = os.path.join(cwd, "events.csv")
## Read the data file using pandas
# data = pd.read_csv(file_path)

## Alternatively, you can import a public CSV file from a URL such as the one below
public_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSS-Stwrw4ikOVAOgK6lzyqhbnC3T6xUynhoVIiA1UYlGQApXy-m12hu4aU2JnweyTV44wkOgK5JKCP/pub?gid=0&single=true&output=csv"
data = pd.read_csv(public_url)


# Define helper functions
def day_difference(start_date, end_date):
    time_remaining = end_date - start_date
    return time_remaining.days


def custom_message(days, event, date, location):
    fmt_day = format_date(date)
    message = f"There are {days} days remaining until {event}."
    message += " " + f"{event} is on {fmt_day}"
    message += " " + f"at {location}."
    if days == 0:
        message = f"{event} is today"
        message += " " + f"at {location}!"
    if days < 0:
        message = f"{event} already passed!" + " "
        message += f"{event} was on {fmt_day}"
        message += " " + f"at {location}."
    return message


def format_date(dob):
    return dob.strftime("%B %d, %Y")


# Create a list of choices
choices = list(data["name"])

# Create the app UI
app_ui = ui.page_fluid(
    # shinyswatch.theme.minty(),
    ui.h1("Event countdown app"),
    ui.navset_tab_card(
        ui.nav(
            "List upcoming",
            ui.input_slider(
                "count", "List a number of upcoming events:", min=1, max=20, value=5
            ),
            ui.output_text_verbatim("count_remaining"),
        ),
        ui.nav(
            "Search event",
            ui.input_selectize("name", "Search an event", choices, selected=None),
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
        # calculate time from now to next event
        today = datetime.today()
        event_date = data[data["name"] == input.name()]["date"].values[0]
        event_date = datetime.strptime(event_date, "%Y-%m-%d")
        days_remaining = day_difference(today, event_date)
        location = data[data["name"] == input.name()]["location"].values[0]
        # return the time remaining in months and days
        return custom_message(days_remaining, input.name(), event_date, location)

    @output
    @render.text
    def count_remaining():
        count_rows = input.count()
        # create a list of tuples with the name and date of event
        events = []
        for index, row in data.iterrows():
            name = row["name"]
            date = datetime.strptime(row["date"], "%Y-%m-%d")
            location = row["location"]
            events.append((name, date, location))

        # calculate the time from now to each event
        today = datetime.today()
        results = []
        for name, date, location in events:
            days_remaining = day_difference(today, date)
            results.append((name, date, days_remaining, location))

        # sort the results by the number of days remaining
        results.sort(key=lambda x: x[2])
        # filter the results to only include the count specified by the user
        results = results[:count_rows]

        # return a list of tuples containing the name and location for each event,
        # along with the number of days remaining to event
        def format_results(results):
            lines = []
            for name, date, days, location in results:
                line = f"{name} will be in {days} days at {location} ({format_date(date)})."
                lines.append(line)
            return "\n".join(lines)

        return format_results(results)


# Create the app
app = App(app_ui, server)
