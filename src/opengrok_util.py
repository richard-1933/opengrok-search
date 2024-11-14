import requests as rq
import time

from Tools.scripts.pathfix import keep_flags
from tqdm import tqdm
from requests.packages.urllib3.exceptions import InsecureRequestWarning

rq.packages.urllib3.disable_warnings(InsecureRequestWarning)

RECORDS_PER_FETCH = 500
url = "https://tpedk02t.wanhai.com/opengrok/api/v1/search"
headers = {
    "Accept": "application/json"
}


def search(qry_payload: dict, fetch_all: bool = False) -> list:
    params = qry_payload.copy()
    params["start"] = 0
    params["maxresults"] = RECORDS_PER_FETCH
    ttl_records = list()
    pbar = tqdm(total=0, desc="Fetching data:", unit="records", leave=True, bar_format='{desc} {n_fmt} records')
    if fetch_all:
        keep_fetching = True
        while keep_fetching:
            tmp_records = _do_fetch_data(params)
            ttl_records += tmp_records
            pbar.update(len(tmp_records))
            if len(tmp_records) == 0:
                keep_fetching = False
            else:
                params["start"] += RECORDS_PER_FETCH

    else:
        ttl_records += _do_fetch_data(params)
        pbar.update(len(ttl_records))
    return ttl_records


def _do_fetch_data(qry_payload: dict) -> list:
    try:
        response = rq.get(url, params=qry_payload, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()["results"]
    except rq.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None
