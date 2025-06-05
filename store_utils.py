import requests

def get_store(riot_id, tag):
    url = f"https://api.henrikdev.xyz/valorant/v1/store/{riot_id}/{tag}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()
    if "data" in data and "skins" in data["data"]:
        return [skin["name"] for skin in data["data"]["skins"]]
    else:
        return []
