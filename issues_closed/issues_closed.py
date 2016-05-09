#!/usr/bin/env python
import sys
import requests
import json
import dateutil.parser
import os
import time
from datetime import date, timedelta

DATA_DIRECTORY = "data"
OUTPUT_DIRECTORY = "output"
GITHUB_BASE_URL = "https://api.github.com/"

def run():
    """
    Generates a report of all closed github issues for repos in `repos.json`
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
    Writes repo issue data to DATA_DIRECTORY, one file per repository.
    Note that the data files saved are temporary and will be deleted at the end of the script.
    """
    print "iterating over repos and saving closed issue data to data files..."
    repos = get_repos()
    for repo in repos:
        issue_data = get_issue_data(repo)

        with open(DATA_DIRECTORY + "/" + repo['owner'] + "_" + repo['name'], 'w') as outfile:
            json.dump(issue_data, outfile)

def get_issue_data(repo):
    """
    Gets issue data for the given repo
    """
    headers = { 'Authorization': 'token ' + get_settings()["github_access_token"] }
    issues_url = GITHUB_BASE_URL + "repos/" + repo['owner'] + "/" + repo['name'] + "/issues?state=closed&per_page=100&since=" + get_report_start_date()
    json_data = []
    while True:
        try:
            response = requests.get(issues_url, headers=headers)
            json_data = json_data + response.json()
            issues_url = get_next_page_url(response)
        except Exception as e:
            # no more pages to retrieve
            break
    return json_data

def get_repos():
    """
    Loads repository data from repos.json into JSON object
    """
    try:
        with open("repos.json") as data_file:    
            repos = json.load(data_file)
        return repos
    except:
        print "Error loading repos.json"
        sys.exit()

def get_next_page_url(response):
    links = parse_link_header(response.headers["link"])
    return links["next"]

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
    report_weeks = get_report_weeks()
    report_end_date = get_report_end_date()
    for week_number in range(0, report_weeks):
        week_end_date = report_end_date - timedelta(days = week_number * 7)
        week_start_date = week_end_date - timedelta(days = 6)
        report_header = "Issues completed from " + week_start_date.strftime("%m/%d/%Y") + " to " + week_end_date.strftime("%m/%d/%Y")
        report.write("==============================================\n")
        report.write(report_header)
        report.write("\n==============================================\n\n")

        for repo_data_file in os.listdir("data"):
            repo_header_added = False

            with open("data/" + repo_data_file) as df:    
                repo_data = json.load(df)

            for issue in repo_data:
                issue_closed_at = dateutil.parser.parse(issue['closed_at']).date()
                if week_end_date >= issue_closed_at >= week_start_date:
                    if not repo_header_added:
                        repo_header = repo_data_file.replace("_", "/")
                        report.write("--------------------------------------\n" + repo_header + ":\n--------------------------------------\n\n")
                        repo_header_added = True
                    line = ("* " + issue['title'] + "\n" + issue['html_url'] + "\n").encode('ascii', 'ignore').decode('ascii')
                    report.write(line)
            if repo_header_added is True: 
                report.write("\n")

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

def get_report_start_date():
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

def get_report_end_date():
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
