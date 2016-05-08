#!/usr/bin/env python
import requests
import json
import dateutil.parser
import os
import time
from datetime import date, timedelta

DATA_DIRECTORY = "data"
OUTPUT_DIRECTORY = "output"
GITHUB_BASE_URL = "https://api.github.com/repos/"

def run(settings, report_weeks, report_start_date, report_end_date):
    """
    Generates a report of all closed github issues for att-projects repos.

    Keyword Arguments:
    settings -- an array of settings variables, derived from `/settings.txt`
    report_weeks -- the number of weeks worth of posts to include in the report
    report_end_date -- datetime.date object representing the end date of the report
    """
    headers = { 'Authorization': 'token ' + settings["github_access_token"] }
    create_directories()
    get_issue_data(headers, report_start_date)
    prepare_issue_report(report_weeks, report_end_date)
    cleanup_data_dir()

def create_directories():
    """
    Creates DATA_DIRECTORY & OUTPUT_DIRECTORY if not exists
    """
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

def get_issue_data(headers, start_date):
    """
    Gets repo issue data and saves to DATA_DIRECTORY, one file per repository.
    Note that the data files saved are temporary and will be deleted.

    Keyword Arguments:
    headers -- headers used when making request to GitHub
    start_date -- all issues closed since this date will be retrieved
    """
    print "iterating over repos and saving closed issue data to data files..."
    repos = get_repos()
    
    for repo in repos:
        issues_url = GITHUB_BASE_URL + repo['owner'] + "/" + repo['name'] + "/issues?state=closed&per_page=100&since=" + start_date
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

def prepare_issue_report(report_weeks, report_end_date):
    """
    Prepares github issue data into a single file report 
    which is timestamped and saved to the OUTPUT_DIRECTORY
    """
    print "preparing report..."
    report = open(OUTPUT_DIRECTORY + "/report-" + time.strftime("%Y-%m-%dT%H:%M:%SZ") + ".txt", 'w')
    i = 0
    while i < report_weeks:
        week_end_date = report_end_date - timedelta(days = i * 7)
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
                if week_end_date >= pr_closed_at > week_end_date - timedelta(days = 7):
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
