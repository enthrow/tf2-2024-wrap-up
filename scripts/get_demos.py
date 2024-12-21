"""
download all of the logs for 2024 from trends.tf (thank you fortybot for letting me hug your API <3)
dump each page into a .json for later processing
"""
import requests
import json
import time

def get_logs(url = "https://trends.tf/api/v1/logs", offset = 1):
    """
    get a page of logs from trends.tf api
    """
    url = "https://trends.tf/api/v1/logs"
    params = {
        "limit": "100",
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "timezone": "America/New_York",
        "view": "players",
        "include_dupes": "no",
        "offset": offset,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return(data)
    else:
        print(f"bad request: {response.status_code}")
        exit() # just so we don't get banned

def dump_log_page(logs, page, output_file = "data/log_dumps/log_page"):
    """
    dump json contents to a file
    """
    output_file += str(page) + ".json"

    with open(output_file, "w") as file:
        json.dump(logs, file, indent=4)

def main():
    offset = 4300 # to start from 0, 0 for both of these.
    pages = 43
    start_time = time.time()
    while True:
        logs = get_logs(offset=offset)
        print(f"got page {pages} of logs.")
        dump_log_page(logs, pages)
        if logs.get("next_page") is not None:
           pages += 1
           offset += 100
           time.sleep(10) # i was getting rate limited even at 8 requests per minute, so go down to 6
        else:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"done! - runtime: {elapsed}")
            break
    
if __name__ == "__main__":
    main()