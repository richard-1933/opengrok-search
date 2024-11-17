import sys
import pandas as pd
import requests as rq
from tqdm import tqdm
from enum import Enum
from requests.packages.urllib3.exceptions import InsecureRequestWarning

rq.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEFAULT_SIZE_PER_FETCH = 500

url = "https://tpedk02t.wanhai.com/opengrok/api/v1/search"

headers = {
    "Accept": "application/json"
}

class FileFormat(Enum):
    EXCEL = 'excel'
    CSV = 'csv'


def save_result_to_file(records: dict, file_format: FileFormat, file_path: str) -> None:
    """
    將查詢結果保存為文件。

    參數:
    results (dict): 查詢結果。
    file_path (str): 文件保存路徑。
    file_format (str): 文件格式，支持'csv'和'excel'，默認為'csv'。
    """
    df = pd.DataFrame.from_dict(records, orient='index')

    if file_format == FileFormat.EXCEL:
        df.to_excel(file_path, index=False, engine='openpyxl')
    elif file_format == FileFormat.CSV:
        df.to_csv(file_path, index=False)
    else:
        raise ValueError("Unsupported file format. Use 'csv' or 'excel'.")

def code_scan(qry_params: dict, start_idx: int = 0, size_per_fetch: int = DEFAULT_SIZE_PER_FETCH,
              fetch_all: bool = False) -> dict:
    """
    執行代碼掃描。

    參數:
    qry_params (dict): 查詢條件。
    start_idx (int): 起始索引，預設為0。
    size_per_fetch (int): 每次抓取的記錄數，預設為RECORDS_PER_FETCH。
    fetch_all (bool): 是否抓取所有記錄，預設為False。

    返回:
    dict: 包含所有抓取記錄的字典。
    """
    params = qry_params.copy()
    params["start"] = start_idx
    params["maxresults"] = size_per_fetch
    ttl_records = dict()
    pbar = tqdm(total=0, desc="Fetching:", file=sys.stdout, unit="records", leave=True,
                bar_format='{desc} {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} records ')
    keep_fetching = True
    while keep_fetching:
        res_data = _do_fetch_data(params)
        resultCnt = res_data["resultCount"]
        tmp_records = res_data["results"]
        ttl_records.update(tmp_records)
        pbar.total = resultCnt
        pbar.update(len(tmp_records.items()))
        if len(tmp_records) == 0 or not fetch_all:
            keep_fetching = False
        else:
            params["start"] += DEFAULT_SIZE_PER_FETCH

    return ttl_records


def _do_fetch_data(qry_payload: dict) -> dict:
    try:
        response = rq.get(url, params=qry_payload, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except rq.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None
