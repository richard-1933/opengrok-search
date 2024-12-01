import argparse, os
import json
import jsonschema
from jsonschema import validate
from opengrok_util import codescan

# 定義 JSON schema
_schema = {
    "type": "object",
    "properties": {
        "full": {"type": "string"},
        "path": {"type": "string"},
        "projects": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["full"]
}


def _validate_query_schema(query_content: str) -> bool:
    """
    驗證json file內容是否符合schema
    :param auery_content:
    :return:
    """
    # 讀取 JSON 文件
    # with open('data.json', 'r') as file:
    data = json.loads(query_content)
    # data = json.load(file)

    # 驗證 JSON 文件內容
    try:
        validate(instance=data, schema=_schema)
        print("JSON 文件內容符合預期")
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(f"JSON 文件內容不符合預期: {err.message}")
        raise

def _non_empty_string(value):
    if not value:
        raise argparse.ArgumentTypeError("This parameter cannot be empty")
    return value


def _convert_query_params(param_dict: dict) -> list[tuple[str, any]]:
    """
    將dict格式查詢參數轉為list[tuple]
    :param param_dict:
    :return:
    """
    params = []
    for key, value in param_dict.items():
        if key == 'projects':
            params.append((key, [proj for proj in value]))
        else:
            params.append((key, value))
    return params

def _handle_scan_process(args: argparse.Namespace):
    url = args.url if args.url else os.getenv('OPENGROK_URL')

    str_qry = None
    if args.query_file:
        with open(os.path.abspath(args.query_file), 'r') as file:
            str_qry = file.read()
    elif args.command_value:
        str_qry = args.command_value

    if _validate_query_schema(str_qry):
        qry_list = _convert_query_params(json.loads(str_qry))
        if args.output_file:
            codescan.scan_to_excel(qry_list, fetch_all=True, export_file=args.output_file, url=url)
        else:
            result = codescan.scan(qry_list, fetch_all=True, url=url)
            print(json.dumps(result, indent=4, ensure_ascii=False))


def main():

    # 建立解析器
    parser = argparse.ArgumentParser(description='opengrok code search tool')
    subparser = parser.add_subparsers(dest="command", help='Sub commands of this utility')

    parser.add_argument('--url', type=_non_empty_string, help='URL of opengrok service')

    parser_scan = subparser.add_parser('scan', help='Code scan utility')
    parser_scan.add_argument('-q', '--query-file', type=_non_empty_string, help='The query file path')
    parser_scan.add_argument('-o', '--output-file', type=_non_empty_string, help='The output file path')
    parser_scan.add_argument('command_value', nargs=argparse.REMAINDER, help='Query parameters')

    args = parser.parse_args()

    command = args.command
    if command == 'scan':
        _handle_scan_process(args)


if __name__ == '__main__':
    main()
