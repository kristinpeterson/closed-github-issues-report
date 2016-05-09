from issues_closed import issues_closed
import sys
from datetime import date

if __name__ == '__main__':
    if(sys.argv[1] == "--help"):
        print "Usage: python main.py <report_weeks> <report_start_date> <report_end_date>"
        print "\t<report_weeks>\t\t(required)\tnumber of weeks to include in the report"
        print "\t<report_start_date>\t(required)\tstart date of report formatted as YYYY-MM-DD"
        print "\t<report_end_date>\t(required)\tend date of report formatted as YYYY-MM-DD"
    else:
        issues_closed.run()
