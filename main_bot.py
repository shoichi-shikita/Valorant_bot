import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os
import json
import aiohttp

# --- 設定読み込み ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
STORE_CHANNEL_ID = int(os.getenv("STORE_CHANNEL_ID", "0"))  # .envに設定 or 手動で数値

# --- Intents 設定 ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

# --- 毎朝 /store を指定チャンネルに送信 ---
async def send_store_command():
    channel = bot.get_channel(STORE_CHANNEL_ID)
    if channel:
        try:
            await channel.send("/store")
            print(f"✅ /store を送信しました: {channel.name}")
        except Exception as e:
            print(f"❌ /store 送信失敗: {e}")
    else:
        print("❌ 指定チャンネルが見つかりません")

# --- Henrik APIを使ってスキンチェック・一致すればDM送信 ---
async def check_store_and_notify():
    if not os.path.exists("data/users.json"):
        print("⚠️ users.json が見つかりません")
        return

    with open("data/users.json", "r") as f:
        users = json.load(f)

    for discord_id, info in users.items():
        riot_id = info.get("riot_id")
        wanted_skins = info.get("skins_wanted", [])

        if not riot_id or not wanted_skins:
            continue

        if "#" not in riot_id:
            print(f"⚠️ 無効な Riot ID: {riot_id}")
            continue

        name, tag = riot_id.split("#")
        url = f"https://api.henrikdev.xyz/valorant/v1/store-offers/{name}/{tag}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"❌ ストア取得失敗: {riot_id}")
                    continue
                data = await resp.json()

        skins_today = [offer["skin"]["name"] for offer in data["data"]["daily"]]
        matched = [skin for skin in wanted_skins if any(skin in s for s in skins_today)]

        if not matched:
            continue

        user = await bot.fetch_user(int(discord_id))
        message = "🎯 今日のストアに以下のスキンがあります！\n" + "\n".join(f"- {m}" for m in matched)
        try:
            await user.send(message)
            print(f"✅ {user} にDM通知しました")
        except Exception as e:
            print(f"❌ DM送信失敗: {e}")

# --- Bot 起動時 ---
@bot.event
async def on_ready():
    print(f"✅ Botログイン成功: {bot.user}")
    scheduler.add_job(send_store_command, 'cron', hour=9, minute=0)
    scheduler.add_job(check_store_and_notify, 'cron', hour=9, minute=0)
    scheduler.start()

# --- 実行 ---
bot.run(TOKEN)