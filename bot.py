import discord
from discord.ext import commands
import os
import pymysql
import firebase_admin
from firebase_admin import credentials, firestore

# .env 파일에서 환경변수 불러오기
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 🔹 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔹 MySQL 연결 설정
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

def connect_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 🔹 Firebase 연결 설정
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 📌 닉네임 저장 (MySQL)
@bot.command(name="닉네임추가")
async def add_nickname(ctx, nickname: str):
    user_id = ctx.author.id
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO nicknames (user_id, nickname) VALUES (%s, %s)", (user_id, nickname))
        connection.commit()
    connection.close()
    await ctx.send(f"✅ 닉네임 `{nickname}` 이(가) 저장되었습니다!")

# 📌 닉네임 검색 (MySQL)
@bot.command(name="닉네임검색")
async def search_nickname(ctx, nickname: str):
    connection = connect_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM nicknames WHERE nickname = %s", (nickname,))
        result = cursor.fetchone()
    connection.close()
    if result:
        await ctx.send(f"🔍 `{nickname}` 닉네임을 가진 유저 ID: `{result['user_id']}`")
    else:
        await ctx.send(f"❌ `{nickname}` 닉네임을 찾을 수 없습니다.")

# 📌 Firebase에서 닉네임 저장
@bot.command(name="닉네임추가_firebase")
async def add_nickname_firebase(ctx, nickname: str):
    user_id = ctx.author.id
    db.collection("nicknames").add({"user_id": user_id, "nickname": nickname})
    await ctx.send(f"✅ 닉네임 `{nickname}` 이(가) Firebase에 저장되었습니다!")

# 📌 Firebase에서 닉네임 검색
@bot.command(name="닉네임검색_firebase")
async def search_nickname_firebase(ctx, nickname: str):
    results = db.collection("nicknames").where("nickname", "==", nickname).get()
    user_ids = [doc.to_dict()["user_id"] for doc in results]
    if user_ids:
        await ctx.send(f"🔍 `{nickname}` 닉네임을 가진 유저 ID: `{', '.join(map(str, user_ids))}`")
    else:
        await ctx.send(f"❌ `{nickname}` 닉네임을 찾을 수 없습니다.")

# 🔹 봇 실행
bot.run(DISCORD_BOT_TOKEN)
