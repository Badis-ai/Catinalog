import discord
from config import ALLOWED_CATEGORIES, CATEGORY_SUBCATEGORIES
from database import cursor
from datetime import datetime

class CategoryDropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=cat) for cat in ALLOWED_CATEGORIES]
        super().__init__(placeholder="Choose a category", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Avoid circular import
        from ui.views import SubcategoryViewNav
        
        category = self.values[0]
        subcats = CATEGORY_SUBCATEGORIES.get(category, [])
        await interaction.response.edit_message(
            content=f"**Category:** {category}\nNow choose a subcategory:",
            view=SubcategoryViewNav(category, subcats)
        )

class SubcategoryDropdown(discord.ui.Select):
    def __init__(self, category, subcategories):
        self.category = category
        options = [discord.SelectOption(label=sub) for sub in subcategories]
        super().__init__(placeholder="Choose a subcategory", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Avoid circular import
        from ui.views import PDFListView
        
        sub = self.values[0]
        await interaction.response.edit_message(
            content=f"**Category:** {self.category}\n**Subcategory:** {sub}\nChoose a PDF:",
            view=PDFListView(self.category, sub)
        )

class CategoryPDFSelect(discord.ui.Select):
    def __init__(self, category, subcategory):
        cursor.execute("""
            SELECT title, author, language, message_id, channel_id, username, date_added 
            FROM pdfs 
            WHERE category = ? AND subcategory = ?
            ORDER BY date_added DESC
        """, (category, subcategory))
        results = cursor.fetchall()

        options = []
        for title, author, language, message_id, channel_id, username, date_added in results:
            label = (title[:50] + '...') if len(title) > 50 else title
            options.append(discord.SelectOption(
                label=label,
                description=f"{author[:20]} - {language}",
                value=f"{channel_id}-{message_id}"
            ))

        if not options:
            options.append(discord.SelectOption(label="No PDFs found", value="none"))

        super().__init__(placeholder="Select a PDF", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("No PDFs available.", ephemeral=True)
            return

        channel_id, message_id = map(int, self.values[0].split("-"))
        cursor.execute("SELECT title, author, username, date_added FROM pdfs WHERE channel_id = ? AND message_id = ?", (channel_id, message_id))
        pdf = cursor.fetchone()

        if pdf:
            title, author, username, date_added = pdf
            link = f"https://discord.com/channels/{interaction.guild.id}/{channel_id}/{message_id}"
            try:
                formatted_date = datetime.fromisoformat(date_added).strftime("%B %d, %Y at %H:%M UTC")
            except:
                formatted_date = date_added

            embed = discord.Embed(title=title, description=f"by {author}", color=discord.Color.green())
            embed.add_field(name="Uploaded by", value=username or "Unknown", inline=True)
            embed.add_field(name="Date", value=formatted_date, inline=True)
            embed.add_field(name="Link", value=f"[Jump to PDF]({link})", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("PDF not found.", ephemeral=True)

