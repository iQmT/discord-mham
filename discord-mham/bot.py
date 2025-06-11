# bot.py

import discord
from discord.ext import commands
import asyncio
from config import TOKEN
from database import init_db
from keep_alive import keep_alive

keep_alive()

init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ✅ سجل الدخول فقط (ما فيه sync هنا)
@bot.event
async def on_ready():
    print(f"✅ سجل الدخول: {bot.user}")


# ✅ استخدم setup_hook لتحميل الإضافات ومزامنة الأوامر
async def setup_hook():
    await bot.load_extension("cogs.inventory")  # اسم الملف صحيح
    await bot.load_extension("cogs.submit")  # إذا عندك ملف ثاني
    synced = await bot.tree.sync()  # ← هنا المزامنة
    print(f"✅ تمت مزامنة {len(synced)} أمر.")


bot.setup_hook = setup_hook


# ✅ main بسيطة بدون تحميل الإضافات (خلاص صارت في setup_hook)
async def main():
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("تم إيقاف البوت بنجاح.")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")
    finally:
        await bot.close()


asyncio.run(main())

bot.run(TOKEN)
