from flask import Flask, render_template, request, redirect
import json
import os
from collections import defaultdict
from store_utils import get_store

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def select_skins():
    user_id = "1234567890"  # 仮のユーザーID（将来Discord OAuthで置換）

    # スキン一覧を読み込み
    with open("data/skins.json", "r", encoding="utf-8") as f:
        skin_list = json.load(f)

    # 武器ごとにスキンを分類
    weapons = defaultdict(list)
    for skin in skin_list:
        weapons[skin["weapon"]].append(skin)

    if request.method == "POST":
        selected = request.form.getlist("skins")

        # ユーザー情報の読み込み
        if os.path.exists("data/users.json"):
            with open("data/users.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        else:
            users = {}

        # スキン保存
        if user_id not in users:
            users[user_id] = {}
        users[user_id]["skins_wanted"] = selected

        with open("data/users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

        return redirect("/success")

    return render_template("skins.html", weapons=weapons)

@app.route("/success")
def success():
    return "✅ スキン登録が完了しました！"

@app.route("/store")
def view_store():
    user_id = "1234567890"  # 仮：Discord OAuth 導入時に置換

    try:
        with open("data/users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        return "⚠️ ユーザーデータが存在しません"

    user = users.get(user_id)
    if not user or "riot_id" not in user or "tag" not in user:
        return "⚠️ Riot ID が登録されていません"

    store = get_store(user["riot_id"], user["tag"])
    if not store:
        return "❌ ストア情報の取得に失敗しました"

    wanted = user.get("skins_wanted", [])
    matched = [skin for skin in store if skin in wanted]

    return render_template("store.html", store=store, matched=matched)

if __name__ == "__main__":
    app.run(debug=True)