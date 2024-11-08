import requests, json, re

url = "https://tpedk02t.wanhai.com/opengrok/api/v1/search"
params = {
    "full": "/.*(sp|sf)\_[a-zA-Z]{3}\_.*/ -type:sh -type:jar -type:javaclass +path:/[a-zA-Z]{3}\_MP/",
    "path": " -\". prc\" -\". fnc\" -\". trg\" -\". tri\" -\". viw\" -\". tab\" -\". pck\" -\". tps\" -/develop -/branch -/IAL -/CNWEB",
    "start": 5200,
    "maxresults": 100
}

headers = {
    "Accept": "application/json"
}

response = requests.get(url, params=params , headers=headers, verify=False)

if response.status_code == 200:
    json_content = response.json()
    pretty_json = json.dumps(json_content, indent=4)
    # json_content = response.json()
    print(pretty_json)

    json_str = json.dumps(json_content)
    matches = re.findall(r'<b>(.*?)</b>', json_str)
    unique_matches = set(matches)
    for match in unique_matches:
        print(match)
else:
    print(f"Failed to retrieve data: {response.status_code}")
