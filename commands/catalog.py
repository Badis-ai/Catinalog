# commands/catalog.py
from discord.ext import commands
from discord import app_commands, Interaction, Embed
import discord
from config import CATEGORY_SUBCATEGORIES, ALLOWED_CATEGORIES
from database import cursor
from ui.views import CatalogView, PDFCatalogueView

class Catalog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="catalog", description="Browse the PDF catalog as an interactive tree")
    async def catalog(self, interaction: Interaction):
        cursor.execute("SELECT COUNT(*) FROM pdfs")
        total_count = cursor.fetchone()[0]
        await interaction.response.send_message(
            f"**📚 PDF Catalogue** - {total_count} total documents\nStart by choosing a category:",
            view=CatalogView(),
            ephemeral=True
        )

    @app_commands.command(name="recent_pdfs", description="View the most recent PDFs added to the collection")
    async def recent_pdfs(self, interaction: Interaction):
        cursor.execute("SELECT COUNT(*) FROM pdfs")
        total_count = cursor.fetchone()[0]
        await interaction.response.send_message(
            f"**📚 Recent PDFs** - {total_count} total documents in the collection\nChoose a PDF to view:",
            view=PDFCatalogueView(),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Catalog(bot))
