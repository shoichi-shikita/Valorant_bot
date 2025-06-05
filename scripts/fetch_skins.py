import requests
import json
import os

url = "https://valorant-api.com/v1/weapons/skins?language=ja-JP"
res = requests.get(url)

if res.status_code != 200:
    print("❌ スキン一覧の取得に失敗しました")
    exit()

data = res.json()
skins = []

for item in data["data"]:
    name = item["displayName"]
    icon = item.get("displayIcon") or item.get("fullRender")
    weapon = item.get("weapon", {}).get("displayName", "その他")

    if name and icon and "ランダム" not in name and "スタンダード" not in name:
        skins.append({
            "name": name,
            "image": icon,
            "weapon": weapon  # 🆕 武器名
        })

# 保存
os.makedirs("data", exist_ok=True)
with open("data/skins.json", "w", encoding="utf-8") as f:
    json.dump(skins, f, indent=2, ensure_ascii=False)

print(f"✅ {len(skins)}件のスキンを保存しました！（武器ごとに分類）")
