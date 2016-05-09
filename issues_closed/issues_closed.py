#!/usr/bin/env python
import sys
import requests
import json
import dateutil.parser
import os
import time
from datetime import date, timedelta

SETTINGS = get_settings()
DATA_DIRECTORY = "data"
OUTPUT_DIRECTORY = "output"
GITHUB_BASE_URL = "https://api.github.com/repos/"
GITHUB_ACCESS_TOKEN = SETTINGS["github_access_token"]
REPORT_WEEKS = get_report_weeks()
REPORT_START_DATE = get_report_start_date_as_ISO_string()
REPORT_END_DATE = get_report_end_date_as_datetime_obj()

def run():
    """
    Generates a report of all closed github issues for att-projects repos.
    """
    create_directories()
    store_issue_data()
    write_issue_report()
    cleanup_data_dir()

def create_directories():
    """
    Creates DATA_DIRECTORY & OUTPUT_DIRECTORY if not exists
    """
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

def store_issue_data():
    """
    Store's repo issue data and saves to DATA_DIRECTORY, one file per repository.
    Note that the data files saved are temporary and will be deleted at the end of the script.
    """
    print "iterating over repos and saving closed issue data to data files..."
    repos = get_repos()
    headers = { 'Authorization': 'token ' + GITHUB_ACCESS_TOKEN }
    
    for repo in repos:
        issues_url = GITHUB_BASE_URL + repo['owner'] + "/" + repo['name'] + "/issues?state=closed&per_page=100&since=" + REPORT_START_DATE
        github_response = requests.get(issues_url, headers=headers)
        
        json_data = github_response.json()
        continue_paging = True

        while continue_paging:
            try:
                links = parse_link_header(github_response.headers['link'])
                github_response = requests.get(links['next'], headers=headers)
                json_data = json_data + github_response.json()
            except Exception:
                continue_paging = False

        with open(DATA_DIRECTORY + "/" + repo['owner'] + "_" + repo['name'], 'w') as outfile:
            json.dump(json_data, outfile)

def get_issue_data(repo):


def get_repos():
    """
    Loads repository data from repos.json into JSON object
    """
    try:
        with open('repos.json') as data_file:    
            repos = json.load(data_file)
        return repos
    except:
        print "Error loading repos.json"
        sys.exit()

def parse_link_header(link):
    """
    Parses the link header in github request

    See: https://developer.github.com/v3/#link-header
    """
    links = {}
    linkHeaders = link.split(", ")
    for linkHeader in linkHeaders:
        (url, rel) = linkHeader.split("; ")
        url = url[1:-1]
        rel = rel[5:-1]
        links[rel] = url
    return links

def write_issue_report():
    """
    Prepares github issue data into a single file report 
    which is timestamped and saved to the OUTPUT_DIRECTORY
    """
    print "preparing report..."
    report = open(OUTPUT_DIRECTORY + "/report-" + time.strftime("%Y-%m-%dT%H:%M:%SZ") + ".txt", 'w')
    i = 0
    while i < REPORT_WEEKS:
        week_end_date = REPORT_END_DATE - timedelta(days = i * 7)
        week_start_date = week_end_date - timedelta(days = 6)
        report_header = "Issues completed from " + week_start_date.strftime("%m/%d/%Y") + " to " + week_end_date.strftime("%m/%d/%Y")
        report.write("==============================================\n")
        report.write(report_header)
        report.write("\n==============================================\n\n")

        for data_file in os.listdir("data"):
            updated = False

            with open("data/" + data_file) as df:    
                data = json.load(df)

            for pr in data:
                pr_closed_at = dateutil.parser.parse(pr['closed_at']).date()
                if week_end_date >= pr_closed_at >= week_start_date:
                    if updated is False:
                        updated = True
                        report.write("--------------------------------------\n" + data_file.replace("_", "/") + ":\n--------------------------------------\n\n")
                    line = ("* " + pr['title'] + "\n" + pr['html_url'] + "\n").encode('ascii', 'ignore').decode('ascii')
                    report.write(line)
            if updated is True: 
                report.write("\n")

        i = i + 1

def cleanup_data_dir():
    """
    Deletes all files in the data directory
    """
    print "cleaning up data directory..."
    file_list = [ f for f in os.listdir(DATA_DIRECTORY) ]
    for f in file_list:
        os.remove(DATA_DIRECTORY + "/" + f)

def get_settings():
    """
    Create a dictionary of settings from settings.txt
    """
    settings = {}
    try:
        with open('settings.txt', 'r') as settings_file:
            for line in settings_file:
                kv = line.partition("=")
                settings[kv[0]] = kv[2].replace("\n", "")
        return settings
    except:
        print "settings.txt missing or not set up properly. Please see README for setup instructions."
        sys.exit()

def get_report_weeks():
    try:
        return int(sys.argv[1])
    except:
        print "<report_weeks> required. Run with '--help' option for usage instructions."
        sys.exit()

def get_report_start_date_as_ISO_string():
    """
    Gets <report_start_date> command line argument and returns the date as an 
    ISO formatted timestamp to be passed to GitHub API when retreiving issues
    """
    try:
        report_start_date = sys.argv[2]
        iso_formatted_timestamp = report_start_date + "T00:00:00Z"
        return iso_formatted_timestamp
    except:
        print "<report_start_date> required. Run with '--help' option for usage instructions."
        sys.exit()

def get_report_end_date_as_datetime_obj():
    """
    Gets the report_end_date and returns it as a datetime object
    """
    try:
        report_end_date = sys.argv[3].split("-")
        year = int(report_end_date[0])
        month =  int(report_end_date[1])
        day = int(report_end_date[2])
        return date(year, month, day)
    except:
        print "<report_end_date> required. Run with '--help' option for usage instructions."
        sys.exit()
