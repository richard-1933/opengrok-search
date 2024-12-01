import os.path
import re
import sys
from enum import Enum
import pandas as pd
import requests as rq
from openpyxl import load_workbook, worksheet
from openpyxl.cell import Cell
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment, Font
from pandas.core.interchange.dataframe_protocol import DataFrame
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm

rq.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEFAULT_SIZE_PER_FETCH = 500

url = "https://tpedk02t.wanhai.com/opengrok/api/v1/search"

headers = {
    "Accept": "application/json"
}

# class FileFormat(Enum):
#     EXCEL = 'excel'
#     CSV = 'csv'


def write_to_excel(data: DataFrame, excel_file_path: str, group_name: str = None) -> None:
    def highlight_content(cell: Cell) -> None:
        pattern = r'(<b>.*</b>)'
        if (cell.value is not None) and re.match(f".*{pattern}.*", cell.value, re.I):
            rich_content = CellRichText()
            for content in re.split(pattern, cell.value, re.I):
                if re.match(pattern, content, re.I):
                    content = re.sub(r'</?b>', '', content)
                    rich_content.append(TextBlock(font=InlineFont(b=True, color='FF0000'), text=content))
                else:
                    rich_content.append(content)
            cell.value = rich_content

    def format_sheet(sheet: worksheet) -> None:
        for col in sheet.columns:
            max_len = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(cell.value) > max_len:
                        max_len = len(cell.value)
                except:
                    pass
            adj_width = (max_len + 2)
            sheet.column_dimensions[column].width = adj_width
            default_font = Font(name='Times New Roman')
            for cell in col:
                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                cell.font = default_font
                highlight_content(cell)

    # Write DataFrame to Excel
    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        if group_name:
            for group_name, group_data in data.groupby(group_name):
                group_data.to_excel(writer, sheet_name=group_name, index=False)
        else:
            data.to_excel(writer, sheet_name='SCAN_RESULT', index=False)

    # Load the workbook and select the active worksheet
    wb = load_workbook(excel_file_path)
    for sheet in wb.worksheets:
        wb.active = sheet
        format_sheet(wb.active)

    # Save the workbook
    wb.save(excel_file_path)
    print(f"File has been saved to: {os.path.abspath(excel_file_path)}")


def scan_to_excel(query_params, start_idx: int = 0, size_per_fetch: int = DEFAULT_SIZE_PER_FETCH,
                  fetch_all: bool = False, export_file: str=os.path.curdir+os.sep+'scan_result.xlsx',**server_config) -> (str, DataFrame):
    records = scan(query_params, start_idx, size_per_fetch, fetch_all, **server_config)
    if records:
        data = []
        for file_path, entries in records.items():
            for entry in entries:
                data.append({
                    "system": re.findall(r"^/([^/]+)/", file_path, re.I)[0],
                    "file_path": file_path,
                    "line": entry['lineNumber'],
                    "content": _remove_illegal_chars(entry['line'])
                })
        df = pd.DataFrame(data)
        print(f"Ttl Scan Results:　{len(records)}, Ttl Output Count: {len(data)}")
        write_to_excel(df, export_file,"system")
        return export_file, df
    else:
        print("No records found.")
        return None, None

def scan(query_params, start_idx: int = 0, size_per_fetch: int = DEFAULT_SIZE_PER_FETCH,
         fetch_all: bool = False, **server_config: dict) -> dict:
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
    _process_server_config(server_config)

    params = None
    if isinstance(query_params, dict):
        params = list(query_params.items())
    else:
        params = list(query_params)

    params.append(('start', start_idx))
    params.append(('maxresults', size_per_fetch))

    ttl_records = dict()
    pbar = tqdm(total=0, desc="Fetching:", file=sys.stdout, unit="records", leave=True, ncols=50,
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
            for i, (key, value) in enumerate(params):
                if key == 'start':
                    params[i] = (key, (value + size_per_fetch))

    return ttl_records


def _process_server_config(server_config):
    """
    處理伺服器設定。
    :param server_config:
    :return:
    """
    global url
    if 'url' in server_config:
        url = server_config['url']


def _remove_illegal_chars(value):
    """
    移除不可列印字元。
    :param value:
    :return:
    """
    if isinstance(value, str):
        return ''.join(c for c in value if c.isprintable() or c == '\n')
    return value

def _do_fetch_data(qry_payload: list) -> dict:
    try:
        response = rq.get(url, params=qry_payload, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except rq.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        raise http_err
    except Exception as err:
        print(f"Other error occurred: {err}")
        raise err
