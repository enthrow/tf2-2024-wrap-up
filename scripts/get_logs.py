"""
download logs from trends.tf as pages of 100 logs each.
(s/o fortybot great site)
dump each page into a .json for later processing
"""
import requests
import json
import time
import argparse

def get_logs(start_date, end_date, timezone, get_dupes, offset):
    """
    get a page of logs from trends.tf api
    """
    url = "https://trends.tf/api/v1/logs"
    params = {
        "limit": "100",
        "date_from": start_date,
        "date_to": end_date,
        "timezone": timezone,
        "view": "players",
        "include_dupes": get_dupes,
        "offset": offset,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return(data)
    else:
        print(f"bad request: {response.status_code}")
        exit() # just so we don't get banned

def dump_log_page(logs, page, output_file):
    """
    dump json contents to a file
    """
    output_file += str(page) + ".json"

    with open(output_file, "w") as file:
        json.dump(logs, file, indent=4)

def main():
    # args
    parser = argparse.ArgumentParser(description='parse log pages from trends.tf for use in react-force-graph')
    parser.add_argument("-sd", "--startdate", type=str, help='start date for query formatted like 2024-01-01')
    parser.add_argument("-ed", "--enddate", type=str, help='end date for query formatted like 2024-01-01')
    parser.add_argument("-tz", "--timezone", type=str, default="America/New_York", help='timezone in standard format for start and end times')
    parser.add_argument("-d", "--dupes", action="store_true", help="if specified, get logs marked as duplicate from trends.tf. defaults false")
    parser.add_argument("-o", "--offset", type=int, required=False, default=0, help="page offset. on what page of 100 logs should we start?")
    parser.add_argument("-p", "--path", type=str, default="data/log_dumps/", help="path to dump logs to. [lognumber].json is appended to this.")
    
    args = parser.parse_args()

    start_date = args.startdate
    end_date = args.enddate
    timezone = args.timezone
    get_dupes = "yes" if args.dupes else "no" # api takes a string don't look at me
    pages = args.offset
    path = args.path

    offset = pages * 100
    start_time = time.time()

    # get all the logs
    while True:
        logs = get_logs(start_date=start_date, end_date=end_date, timezone=timezone, get_dupes=get_dupes, offset=offset)
        print(f"got page {pages} of logs.")
        dump_log_page(logs, pages, path)
        if logs.get("next_page") is not None:
           pages += 1
           offset += 100
           time.sleep(10) # don't get rate limited, tried lower, didn't help
        else:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"done! - runtime: {elapsed}")
            break
    
if __name__ == "__main__":
    main()