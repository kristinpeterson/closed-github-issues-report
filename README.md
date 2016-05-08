## Closed GitHub Issues Report

The purpose of this script is to prepare a report of all GitHub issues closed for a set of repositories over a given timeframe. The resulting report is segmented by week.

Example Report Output: https://gist.github.com/kristinpeterson/a97543e792ed82d9ba1a7adc366e1eba

### How to specify which repositories to include in the report

Create a file called `repos.json` and store it in the root of the project, see [`repos.sample`](repos.sample) for an example. Each library is represented as a JSON object with the following structure:

```
{ 
  "name": "repo-name",
  "owner": "repo-owner"
}
```

### Prerequisites

A GitHub [access token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) from an account that has `PULL` access to the target repositories must be created.

1. Go to: https://github.com/settings/tokens
2. Generate an token with access to the following scopes: `repo` and `public_repo`
3. Make a copy of [`settings.sample`](settings.sample) and rename to `settings.txt`
4. Assign the access token created in step 2 to `github_access_token` in `settings.txt`, Example:

```
github_access_token=[GITHUB_ACCESS_TOKEN_HERE]
```

### Dependencies

See [`requirements.txt`](/requirements.txt) for dependency list. I suggest using [`virtualenv`](https://virtualenv.readthedocs.org/en/latest/) to manage your dependencies.

### Usage

1. Confirm that the repos listed in `repos.json` are accurate
2. Run the script from the root directory of the project: 

```
python main.py <report_weeks> <report_start_date> <report_end_date>
```

Command line arguments:

* `report_weeks` (required) number of weeks to include in the report
* `report_start_date` (required) start date of report formatted as YYYY-MM-DD (Monday)
* `report_end_date` (required) end date of report formatted as YYYY-MM-DD (Sunday)
