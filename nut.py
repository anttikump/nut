#!/usr/bin/env python3

import csv
from datetime import datetime, timedelta, time
from dateutil.parser import parse
import re
import logging
import argparse
from glob import glob
from os import path

logging.basicConfig(level='INFO', format='%(message)s')
LOGGER = logging.getLogger("nutter")

HOURLY_WAGE   = 3.75
EVENING_BONUS = 1.15


class TimeInterval:
    def __init__(self, _start, _end):
        self.start = _start
        self.end   = _end
    def days(self):
        return {self.start.date(), self.end.date()}
    def hours(self):
        return (self.end - self.start).total_seconds() / 3600
    def intersection(self, other):
        return TimeInterval(max(self.start, other.start), min(self.end, other.end))


def overtime(h): # (0-8, 0) (8-10, 25) (10-12, 50) (12->, 100)
    return max(h-8, 0) * .25 + max(h-10, 0) * .25 + max(h-12, 0) *.50


def evening_hours(time_interval):
    def daytime_hours(day):
        start = datetime.combine(day, time( 6,00))
        end   = datetime.combine(day, time(18,00))
        return max(TimeInterval(start, end).intersection(time_interval).hours(), 0)
    return time_interval.hours() - sum(daytime_hours(day) for day in time_interval.days())


class Person:
    def __init__(self, _name):
        MAX_DAYS_IN_MONTH = 35
        self.name = _name
        self.days = [[] for i in range(MAX_DAYS_IN_MONTH)]
    def add_work_shift(self, interval):
        day = interval.start.date().day
        self.days[day].append(interval)
    def total_wage(self):
        regular_wage          = 0
        evening_compensation  = 0
        overtime_compensation = 0
        for d in self.days:
            if d:
                total_hours = sum(i.hours() for i in d)
                regular_wage          += total_hours * HOURLY_WAGE
                evening_compensation  += sum(evening_hours(i) for i in d) * EVENING_BONUS
                overtime_compensation += overtime(total_hours) * HOURLY_WAGE
        return regular_wage + evening_compensation + overtime_compensation


def read_hourlist(csv_file_name):
    persons = {}

    with open(csv_file_name) as f:
        reader = csv.DictReader(f)
        for row in reader:
            date  = parse(row['Date'],  dayfirst=True)
            start = parse(row['Start'], default=date)
            end   = parse(row['End'],   default=date)
            if (end < start):
                end += timedelta(days = 1)

            interval = TimeInterval(start, end)
            uid      = int(row['Person ID'])
            if not uid in persons:
                persons[uid] = Person(row['Person Name'])

            persons[uid].add_work_shift(interval)

    return persons


def write_report(persons, csv_file_name):
    with open(csv_file_name, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["ID","NAME","TOTAL"])
        writer.writeheader()
        LOGGER.debug(">\tID  NAME            TOTAL")
        for uid in sorted(persons.keys()):
            name = persons[uid].name
            wage = persons[uid].total_wage()
            writer.writerow({"ID":uid, "NAME":name, "TOTAL":wage})
            LOGGER.debug(">\t{:<3d} {:15s} ${:.2f}".format(uid, name, wage))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="An hourlist csv parser",
        epilog="This is how we parse"
    )
    parser.add_argument("input",  type=str, help="input file or files")
    parser.add_argument("output", type=str, help="output folder for report files")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        LOGGER.setLevel('DEBUG')

    for ifile in glob(args.input):
        LOGGER.info("="*50)
        persons = read_hourlist(ifile)
        LOGGER.info("Read  '{}'".format(ifile))

        timestamp = re.compile(r"\d+").search(ifile)[0]
        ofile = path.join(args.output, "Report{}.csv".format(timestamp))

        persons = read_hourlist(ifile)
        write_report(persons, ofile)
        LOGGER.info("Wrote '{}'".format(ofile))
        LOGGER.info("="*50)
