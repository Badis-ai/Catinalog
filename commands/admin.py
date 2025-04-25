# commands/admin.py
from discord.ext import commands
from discord import app_commands, Interaction, File
from config import ALLOWED_CATEGORIES, CATEGORY_DESCRIPTIONS, CATEGORY_EMOJIS
from database import cursor
import json, asyncio
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="addcategory", description="Admin: add a new category")
    @app_commands.checks.has_permissions(administrator=True)
    async def addcategory(self, interaction: Interaction, category: str, emoji: str):
        if category in ALLOWED_CATEGORIES:
            await interaction.response.send_message("Category already exists.", ephemeral=True)
        else:
            ALLOWED_CATEGORIES.append(category)
            CATEGORY_EMOJIS[category] = emoji
            CATEGORY_DESCRIPTIONS[category] = "No description provided yet."
            await interaction.response.send_message(f"✅ Added **{category}** with emoji {emoji}.", ephemeral=True)

    @app_commands.command(name="topcollectors", description="See who uploaded the most PDFs")
    async def topcollectors(self, interaction: Interaction):
        cursor.execute("""
            SELECT username, user_id, COUNT(*) as count 
            FROM pdfs 
            WHERE user_id IS NOT NULL 
            GROUP BY user_id 
            ORDER BY count DESC 
            LIMIT 10
        """)
        results = cursor.fetchall()

        if not results:
            await interaction.response.send_message("No uploads found.", ephemeral=True)
            return

        msg = "# 📚 Top PDF Uploaders 📚\n\n"
        for i, (user, uid, count) in enumerate(results, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
            msg += f"{emoji} **{i}.** {user or f'User {uid}'}: **{count}** PDFs\n"

        await interaction.response.send_message(msg)
        await asyncio.sleep(180)
        try:
            await (await interaction.original_response()).delete()
        except:
            pass

    @app_commands.command(name="dumpjson", description="Admin: export DB to JSON")
    @app_commands.checks.has_permissions(administrator=True)
    async def dumpjson(self, interaction: Interaction):
        try:
            cursor.execute("SELECT title, author, category, subcategory, language, date_added, username FROM pdfs")
            data = cursor.fetchall()
            json_data = [
                {
                    "title": t, "author": a, "category": c,
                    "subcategory": s, "language": l,
                    "date_added": d, "added_by": u or "Unknown"
                } for t, a, c, s, l, d, u in data
            ]
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

            with open("pdf_export.json", "w", encoding="utf-8") as f:
                f.write(json_str)

            await interaction.response.send_message("Exported database as JSON:", file=File("pdf_export.json"), ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))