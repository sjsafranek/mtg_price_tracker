import requests


def checkError(resp):
    if 200 != resp.status_code:
        print(resp.text)
        exit(1)


def fetchJSON(url):
    resp = requests.get(url)
    checkError(resp)
    return resp.json()
