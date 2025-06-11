# cogs/submit.py

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from views import CategorySelectView
import io


class Submit(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    ALLOWED_CHANNEL_ID = 1382409282733215764  # استبدل هذا بالآيدي الحقيقي

    @app_commands.command(name="ارسال", description="أرسل صورة وسيتم مراجعتها")
    async def ارسال(self, interaction: discord.Interaction):
        if interaction.channel.id != self.ALLOWED_CHANNEL_ID:
            return await interaction.response.send_message(
                "❌ هذا الأمر مسموح فقط في شات <#1382409282733215764>.",
                ephemeral=True)
        await interaction.response.send_message(
            "📷 أرسل الصورة كمرفق (وليس كرابط) خلال 60 ثانية:", ephemeral=True)

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel.id == interaction.channel.id

        try:
            msg = await self.bot.wait_for("message", timeout=60.0, check=check)

            if not msg.attachments:
                return await interaction.followup.send(
                    "❌ لازم ترسل صورة كمرفق.", ephemeral=True)

            attachment = msg.attachments[0]
            if not attachment.content_type or not attachment.content_type.startswith(
                    "image/"):
                return await interaction.followup.send(
                    "❌ الملف المرسل ليس صورة.", ephemeral=True)

            # ✅ قراءة الصورة من المرفق
            image_bytes = await attachment.read()
            file = discord.File(fp=io.BytesIO(image_bytes),
                                filename="image.png")

            # ✅ إعداد الرسالة مع صورة داخلية
            embed = discord.Embed(
                title="طلب جديد للمراجعة",
                description=f"🧾 تم الإرسال بواسطة: {interaction.user.mention}",
                color=discord.Color.purple())
            embed.set_image(url="attachment://image.png")

            view = CategorySelectView(interaction.user, embed)

            # ✅ إرسال الرسالة الجديدة مع الملف والـ Embed بدون تكرار
            await interaction.channel.send(embed=embed, view=view, file=file)

            await interaction.followup.send(
                "✅ تم استلام الصورة وجاري مراجعتها.", ephemeral=True)

            await msg.delete()

        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ انتهى الوقت، ما استلمت صورة.",
                                            ephemeral=True)


async def setup(bot):
    await bot.add_cog(Submit(bot))
