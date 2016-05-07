from issues_closed import issues_closed
import sys
from datetime import date

def get_settings():
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
        report_end_date = sys.argv[2]
        iso_formatted_timestamp = report_end_date + "T00:00:00Z"
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

if __name__ == '__main__':
    if(sys.argv[1] == "--help"):
        print "Usage: python main.py <report_weeks> <report_start_date> <report_end_date>"
        print "\t<report_weeks>\t\t(required)\tnumber of weeks to include in the report"
        print "\t<report_start_date>\t(required)\tstart date of report formatted as YYYY-MM-DD"
        print "\t<report_end_date>\t(required)\tend date of report formatted as YYYY-MM-DD"
    else:
        issues_closed.run(get_settings(), get_report_weeks(), get_report_start_date(), get_report_end_date())
