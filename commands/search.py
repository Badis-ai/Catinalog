# commands/search.py
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import discord
import re
from config import ALLOWED_LANGUAGES, ALLOWED_CATEGORIES, CATEGORY_EMOJIS
from database import cursor
from ui.views import PdfNavigationView

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="searchpdf", description="Search PDFs naturally")
    @app_commands.describe(query="Ask naturally like 'Philosophy books in English' or 'Math by John'")
    async def searchpdf(self, interaction: Interaction, query: str):
        await interaction.response.defer(ephemeral=True)
        query_lower = query.lower()
        clauses = []
        values = []

        for cat in ALLOWED_CATEGORIES:
            if cat.lower() in query_lower:
                clauses.append("category LIKE ?")
                values.append(f"%{cat}%")

        for lang in ALLOWED_LANGUAGES:
            if lang in query_lower:
                clauses.append("language LIKE ?")
                values.append(f"%{lang}%")

        match_author = re.search(r"by ([a-zA-Z\s]+)", query)
        if match_author:
            values.append(f"%{match_author.group(1).strip()}%")
            clauses.append("author LIKE ?")

        match_title = re.search(r"called ([a-zA-Z\s]+)", query)
        if match_title:
            values.append(f"%{match_title.group(1).strip()}%")
            clauses.append("title LIKE ?")

        if not clauses:
            clauses.append("title LIKE ? OR author LIKE ?")
            values += [f"%{query}%", f"%{query}%"]

        query_str = " OR ".join(clauses)
        cursor.execute(f"SELECT title, author, category, subcategory, language, channel_id, message_id, username FROM pdfs WHERE {query_str}", tuple(values))
        results = cursor.fetchall()

        if not results:
            await interaction.followup.send("No matches found.", ephemeral=True)
            return

        await interaction.followup.send(
            embed=self.build_embed(results, query, interaction.guild.id),
            view=PdfNavigationView(results, query, interaction.guild.id),
            ephemeral=True
        )

    def build_embed(self, results, query, guild_id):
        embed = Embed(
            title=f"Search Results for '{query}'",
            description=f"Showing top {min(len(results), 20)} results",
            color=discord.Color.blue()
        )
        for i, (title, author, category, subcategory, language, ch, msg, username) in enumerate(results[:5], 1):
            link = f"https://discord.com/channels/{guild_id}/{ch}/{msg}"
            embed.add_field(
                name=f"{i}. {title} by {author}",
                value=f"Category: {category} > {subcategory or 'N/A'} | Language: {language}\n[Jump to PDF]({link})",
                inline=False
            )
        return embed

async def setup(bot):
    await bot.add_cog(Search(bot))
