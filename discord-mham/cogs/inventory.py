import discord
from discord.ext import commands
from discord import app_commands
from config import ALLOWED_ROLE_NAMES
from database import (
    get_all_approvals_grouped,
    delete_all_approvals,
    delete_user_category,
    add_multiple_approvals,
    get_user_approvals
)

LOG_CHANNEL_ID = 1382409456461283479  # آيدي شات اللوقات

# ✅ قائمة الفئات (خارج الكلاس)
CATEGORIES = [
    app_commands.Choice(name="تجنيد", value="تجنيد"),
    app_commands.Choice(name="حساب عسكري الأسبوع او ضابط الفتره", value="حساب عسكري الأسبوع او ضابط الفتره"),
    app_commands.Choice(name="تكت او شكوى في المجلس", value="تكت او شكوى في المجلس"),
    app_commands.Choice(name="الإجازات والإستقالات", value="الإجازات والإستقالات"),
    app_commands.Choice(name="الترقيات والتقارير الإشرافيه", value="الترقيات والتقارير الإشرافيه"),
]

class ConfirmDeleteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="✅ تأكيد الحذف", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.name in ALLOWED_ROLE_NAMES for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 ما عندك صلاحية.", ephemeral=True)
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"🗑️ **تم حذف كل بيانات الجرد** بواسطة {interaction.user.mention}"
            )

        delete_all_approvals()
        await interaction.response.edit_message(content="✅ تم حذف جميع بيانات الجرد.", view=None)

    @discord.ui.button(label="❌ إلغاء", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ تم الإلغاء.", view=None)


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    MOD_CHANNEL_ID = 1319812578511163455  # شات المشرفين

    @app_commands.command(name="جرد", description="عرض الجرد")
    async def جرد(self, interaction: discord.Interaction):
        if interaction.channel.id != self.MOD_CHANNEL_ID:
            return await interaction.response.send_message("❌ هذا الأمر مخصص لشات المشرفين فقط.", ephemeral=True)
        if not any(role.name in ALLOWED_ROLE_NAMES for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 للمشرفين فقط", ephemeral=True)

        data = get_all_approvals_grouped()
        if not data:
            return await interaction.response.send_message("❌ لا توجد بيانات حالياً.", ephemeral=True)

        user_data = {}
        for user_id, category, count in data:
            if user_id not in user_data:
                user_data[user_id] = []
            user_data[user_id].append(f"{count} : {category}")

        embed = discord.Embed(title="📋 جرد الطلبات", color=discord.Color.dark_blue())
        for i, (user_id, entries) in enumerate(user_data.items(), start=1):
            user_mention = f"<@{user_id}>"
            embed.add_field(
                name=f"👤 العسكري {i}",
                value=f"{user_mention} (`{interaction.user.id}`)\n" + "\n".join(entries),
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="جردي", description="اطلع الجرد الخاص بك")
    async def جردي(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        results = get_user_approvals(user_id)
        if not results:
            return await interaction.response.send_message("❌ ما عندك طلبات في السجل.", ephemeral=True)

        embed = discord.Embed(
            title="📦 الجرد الشخصي",
            description=f"عرض عدد الطلبات المرسلة بواسطة {interaction.user.mention}",
            color=discord.Color.teal()
        )

        for category, count in results:
            embed.add_field(name=category, value=f"`{count}` طلب", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="حذف_الجرد", description="حذف الجرد للمشرفين")
    async def حذف_الجرد(self, interaction: discord.Interaction):
        if interaction.channel.id != self.MOD_CHANNEL_ID:
            return await interaction.response.send_message("❌ هذا الأمر مخصص لشات المشرفين فقط.", ephemeral=True)
        if not any(role.name in ALLOWED_ROLE_NAMES for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 للمشرفين فقط", ephemeral=True)

        view = ConfirmDeleteView()
        await interaction.response.send_message("⚠️ تأكيد حذف الجرد؟", view=view, ephemeral=True)

    @app_commands.command(name="تعديل_الجرد", description="تعديل عدد الطلبات")
    @app_commands.describe(user="المستخدم", category="الفئة", new_count="العدد الجديد")
    @app_commands.choices(category=CATEGORIES)
    async def تعديل_الجرد(self, interaction: discord.Interaction, user: discord.User, category: app_commands.Choice[str], new_count: int):
        if not any(role.name in ALLOWED_ROLE_NAMES for role in interaction.user.roles):
            if interaction.channel.id != self.MOD_CHANNEL_ID:
                return await interaction.response.send_message("❌ هذا الأمر مخصص لشات المشرفين فقط.", ephemeral=True)
            return await interaction.response.send_message("🚫 للمشرفين فقط", ephemeral=True)

        delete_user_category(user.id, category.value)
        add_multiple_approvals(user.id, new_count, interaction.user.id, category.value)

        await interaction.response.send_message(
            f"✅ تم التعديل لـ {user.mention} في {category.name} إلى {new_count}", ephemeral=True
        )

        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"✏️ **تعديل الجرد:** {interaction.user.mention} عدّل بيانات <@{user.id}> في فئة `{category.name}` إلى `{new_count}`"
            )


async def setup(bot):
    await bot.add_cog(Inventory(bot))
