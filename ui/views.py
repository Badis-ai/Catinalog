# ui/views.py
import discord
from discord.ui import View
from config import ALLOWED_CATEGORIES
from database import cursor
from datetime import datetime

from ui.selects import CategoryDropdown, SubcategoryDropdown, CategoryPDFSelect

class CatalogView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(CategoryDropdown())

class SubcategoryViewNav(View):
    def __init__(self, category, subcategories):
        super().__init__(timeout=180)
        self.add_item(SubcategoryDropdown(category, subcategories))

class PDFListView(View):
    def __init__(self, category, subcategory):
        super().__init__(timeout=180)
        self.add_item(CategoryPDFSelect(category, subcategory))

class PDFCatalogueView(View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(PDFSelect())

class PDFSelect(discord.ui.Select):
    def __init__(self):
        cursor.execute("SELECT title, author, category, subcategory, language, message_id, channel_id, username, date_added FROM pdfs ORDER BY date_added DESC LIMIT 20")
        results = cursor.fetchall()

        options = []
        for title, author, category, subcategory, language, message_id, channel_id, username, date_added in results:
            label = (title[:35] + '...') if len(title) > 35 else title
            description = f"{author[:15]} - {category}" + (f" > {subcategory}" if subcategory else "") + f" ({language})"
            options.append(discord.SelectOption(label=label, value=f"{channel_id}-{message_id}", description=description))

        if not options:
            options.append(discord.SelectOption(label="No PDFs found", value="none"))

        super().__init__(placeholder="Choose a PDF to view...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("No PDFs available.", ephemeral=True)
            return

        channel_id, message_id = map(int, self.values[0].split("-"))
        cursor.execute("SELECT title, author, subcategory, username, date_added FROM pdfs WHERE channel_id = ? AND message_id = ?", (channel_id, message_id))
        pdf = cursor.fetchone()

        if pdf:
            title, author, subcategory, username, date_added = pdf
            link = f"https://discord.com/channels/{interaction.guild.id}/{channel_id}/{message_id}"
            try:
                formatted_date = datetime.fromisoformat(date_added).strftime("%B %d, %Y at %H:%M UTC")
            except:
                formatted_date = date_added

            subcat = f"\nSubcategory: {subcategory}" if subcategory else ""
            await interaction.response.send_message(
                f"**{title}** by *{author}*{subcat}\nUploaded by: {username} on {formatted_date}\n[Jump to PDF]({link})",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("PDF details not found.", ephemeral=True)

class PdfNavigationView(View):
    def __init__(self, results, query, guild_id):
        super().__init__(timeout=180)
        self.results = results
        self.query = query
        self.guild_id = guild_id
        self.current_page = 0
        self.total_pages = max(1, (len(results) + 4) // 5)
        
        # Add our buttons with fixed callbacks
        self.prev_button = discord.ui.Button(label="◀️ Previous", style=discord.ButtonStyle.gray, custom_id="prev")
        self.prev_button.callback = self.previous_callback
        self.add_item(self.prev_button)
        
        self.next_button = discord.ui.Button(label="▶️ Next", style=discord.ButtonStyle.gray, custom_id="next")
        self.next_button.callback = self.next_callback
        self.add_item(self.next_button)

        # Create dropdown for jumping to results
        self.jump_select = discord.ui.Select(
            placeholder="Jump to a result...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label=f"{i+1}. {res[0][:40]}", description=f"By {res[1][:30]}", value=str(i))
                for i, res in enumerate(results[:20])
            ]
        )
        self.jump_select.callback = self.jump_callback
        self.add_item(self.jump_select)

    async def previous_callback(self, interaction: discord.Interaction):
        self.current_page = max(0, self.current_page - 1)
        await self.update_message(interaction)

    async def next_callback(self, interaction: discord.Interaction):
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        await self.update_message(interaction)
        
    async def jump_callback(self, interaction: discord.Interaction):
        selected_index = int(self.jump_select.values[0])
        self.current_page = selected_index // 5
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"Results for '{self.query}'",
            description=f"Page {self.current_page+1}/{self.total_pages}",
            color=discord.Color.blue()
        )
        page = self.results[self.current_page * 5 : (self.current_page + 1) * 5]
        for i, (title, author, category, subcategory, lang, ch, msg, username) in enumerate(page, 1):
            link = f"https://discord.com/channels/{self.guild_id}/{ch}/{msg}"
            embed.add_field(
                name=f"{i}. {title} by {author}",
                value=f"Category: {category} > {subcategory or 'N/A'} | Language: {lang}\n[Jump to PDF]({link})",
                inline=False
            )
        await interaction.response.edit_message(embed=embed, view=self)
