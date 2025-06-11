# views.py

import discord
from config import ALLOWED_ROLE_NAMES
from database import insert_approval

LOG_CHANNEL_ID = 1382409456461283479  # آيدي شات اللوقات


class ApprovalView(discord.ui.View):

    def __init__(self, original_user: discord.User, category: str):
        super().__init__(timeout=None)
        self.original_user = original_user
        self.category = category

    @discord.ui.button(label="✅ قبول", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        if not any(role.name in ALLOWED_ROLE_NAMES
                   for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 ما عندك صلاحية",
                                                           ephemeral=True)
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"✅ **تم قبول الطلب** من <@{self.original_user.id}>\n\n بواسطة {interaction.user.mention}\n\n في التصنيف `{self.category}`"
            )

        embed = interaction.message.embeds[0]
        if "تم القبول" in embed.description or "تم الرفض" in embed.description:
            return await interaction.response.send_message(
                "⚠️ هذا الطلب تم التعامل معه مسبقًا.", ephemeral=True)

        embed.description += f"\n\n✅ **تم القبول بواسطة** {interaction.user.mention}"
        await interaction.message.edit(embed=embed, view=None, attachments=[])
        insert_approval(self.original_user.id, "accepted", interaction.user.id,
                        self.category)
        await interaction.response.send_message("✅ تم القبول", ephemeral=True)

    @discord.ui.button(label="❌ رفض", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        if not any(role.name in ALLOWED_ROLE_NAMES
                   for role in interaction.user.roles):
            return await interaction.response.send_message("🚫 ما عندك صلاحية",
                                                           ephemeral=True)
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"❌ **تم رفض الطلب** من <@{self.original_user.id}>\n\n بواسطة {interaction.user.mention}\n\n في التصنيف `{self.category}`"
            )
        embed = interaction.message.embeds[0]
        if "تم القبول" in embed.description or "تم الرفض" in embed.description:
            return await interaction.response.send_message(
                "⚠️ هذا الطلب تم التعامل معه مسبقًا.", ephemeral=True)

        embed.description += f"\n\n❌ **تم الرفض بواسطة** {interaction.user.mention}"
        await interaction.message.edit(embed=embed, view=None, attachments=[])
        await interaction.response.send_message("❌ تم الرفض", ephemeral=True)


class CategorySelectView(discord.ui.View):

    def __init__(self, interaction_user: discord.User, embed: discord.Embed):
        super().__init__(timeout=60)
        self.interaction_user = interaction_user
        self.embed = embed

    @discord.ui.select(
        placeholder="اختر نوع الطلب...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="تجنيد", value="تجنيد"),
            discord.SelectOption(label="حساب عسكري الأسبوع او ضابط الفتره",
                                 value="حساب عسكري الأسبوع او ضابط الفتره"),
            discord.SelectOption(label="تكت او شكوى في المجلس",
                                 value="تكت او شكوى في المجلس"),
            discord.SelectOption(label="الإجازات والإستقالات",
                                 value="الإجازات والإستقالات"),
            discord.SelectOption(label="الترقيات والتقارير الإشرافيه",
                                 value="الترقيات والتقارير الإشرافيه"),
        ])
    async def select_callback(self, interaction: discord.Interaction,
                              select: discord.ui.Select):
        if interaction.user != self.interaction_user:
            return await interaction.response.send_message(
                "❌ هذا الخيار مو لك.", ephemeral=True)

        selected_category = select.values[0]
        self.embed.description += f"\n\n📂 النوع: `{selected_category}`"
        from views import ApprovalView
        await interaction.message.edit(embed=self.embed,
                                       view=ApprovalView(
                                           self.interaction_user,
                                           selected_category))
        await interaction.response.defer()
