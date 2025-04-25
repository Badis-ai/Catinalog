# commands/pdf_management.py
from discord.ext import commands
from discord import app_commands, Interaction
import discord
import re, os, hashlib, asyncio
from utils.pdf_utils import generate_preview
from database import cursor
from config import PDF_CHANNEL_ID

class PDFManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="preview", description="Generate a preview of a PDF file")
    @app_commands.describe(pdf_url="Link to the PDF message in Discord")
    async def preview(self, interaction: Interaction, pdf_url: str = None):
        await interaction.response.defer(ephemeral=True)

        pdf_attachment = None
        pdf_data = {}

        # Try to extract attachment
        if pdf_url:
            match = re.search(r'channels/\d+/(\d+)/(\d+)', pdf_url)
            if match:
                channel_id, message_id = int(match.group(1)), int(match.group(2))
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    await interaction.followup.send("Invalid channel.")
                    return
                message = await channel.fetch_message(message_id)
                pdf_attachment = next((a for a in message.attachments if a.filename.endswith('.pdf')), None)
                cursor.execute("SELECT title, author, category, subcategory, language FROM pdfs WHERE message_id = ?", (message_id,))
                info = cursor.fetchone()
                if not info:
                    await interaction.followup.send("Not found in DB.", ephemeral=True)
                    return
                pdf_data = dict(zip(["title", "author", "category", "subcategory", "language"], info))

        if not pdf_attachment:
            await interaction.followup.send("No PDF found in the message.", ephemeral=True)
            return

        temp_dir = "temp_pdfs"
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs("thumbnails", exist_ok=True)
        temp_path = f"{temp_dir}/{pdf_attachment.filename}"
        await pdf_attachment.save(temp_path)

        preview_data = generate_preview(temp_path, pdf_attachment.filename)
        os.remove(temp_path)

        embed = discord.Embed(
            title=f"Preview: {pdf_data['title']}",
            description=f"By {pdf_data['author']}",
            color=discord.Color.blue()
        )

        file = None
        if preview_data["thumbnail"]:
            file = discord.File(preview_data["thumbnail"], filename="thumb.jpg")
            embed.set_thumbnail(url="attachment://thumb.jpg")

        if preview_data["excerpt"]:
            embed.add_field(name="Excerpt", value=preview_data["excerpt"], inline=False)

        if preview_data["toc"]:
            toc = "\n".join(["  " * e["level"] + f"• {e['title']}" for e in preview_data["toc"][:5]])
            embed.add_field(name="Table of Contents", value=toc + ("\n..." if len(preview_data["toc"]) > 5 else ""), inline=False)

        embed.add_field(name="Category", value=f"{pdf_data['category']} > {pdf_data['subcategory']}", inline=True)
        embed.add_field(name="Language", value=pdf_data['language'], inline=True)

        await interaction.followup.send(embed=embed, file=file if file else None, ephemeral=True)

        if preview_data["thumbnail"]:
            os.remove(preview_data["thumbnail"])

async def setup(bot):
    await bot.add_cog(PDFManagement(bot))
