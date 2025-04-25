from discord.ext import commands
import discord
from discord import Embed
from database import cursor, insert_pdf
from config import ALLOWED_LANGUAGES, ALLOWED_CATEGORIES, CATEGORY_SUBCATEGORIES, PDF_CHANNEL_ID
from utils.file_utils import get_file_hash, delete_after_delay

class PDFUpload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for PDF uploads and process them"""
        if message.channel.id != PDF_CHANNEL_ID:
            return
        
        if message.author.bot:
            return
        
        pdf_attachments = [a for a in message.attachments if a.filename.lower().endswith('.pdf')]
        if not pdf_attachments:
            return
        
        for attachment in pdf_attachments:
            file_info = {
                "filename": attachment.filename,
                "url": attachment.url,
                "size": attachment.size,
                "message_id": message.id,
                "channel_id": message.channel.id,
                "user_id": message.author.id,
                "username": str(message.author)
            }
            
            file_hash = await get_file_hash(attachment)
            file_info["file_hash"] = file_hash
            
            cursor.execute("SELECT title, author FROM pdfs WHERE file_hash = ?", (file_hash,))
            existing = cursor.fetchone()
            
            if existing:
                title, author = existing
                embed = Embed(
                    title="⚠️ Duplicate Detected",
                    description=f"This file appears to be a duplicate of **{title}** by *{author}*",
                    color=discord.Color.yellow()
                )
                response = await message.reply(embed=embed)
                await delete_after_delay(response, 30)
                continue
            
            # Create a button to start the metadata entry
            class UploadButton(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=3600)  # 1 hour timeout
                
                @discord.ui.button(label=f"Add metadata for {attachment.filename[:20]}...", style=discord.ButtonStyle.primary)
                async def metadata_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id != message.author.id:
                        await interaction.response.send_message("Only the uploader can add metadata.", ephemeral=True)
                        return
                    
                    # Start the metadata collection
                    await interaction.response.send_message("Please enter the **title** of the PDF:", ephemeral=True)
                    await self.collect_title(interaction, file_info)
            
            # Send the button
            await message.reply(f"Please add metadata for your PDF upload:", view=UploadButton())

    async def collect_title(self, interaction, file_info):
        # Wait for the title input
        def check(msg):
            return msg.author == interaction.user and isinstance(msg.channel, discord.abc.Messageable)
        
        title_msg = await self.bot.wait_for('message', check=check)
        title = title_msg.content
        
        # Ask for author
        await interaction.followup.send("Please enter the **author** of the PDF:", ephemeral=True)
        author_msg = await self.bot.wait_for('message', check=check)
        author = author_msg.content
        
        # Ask for category
        await interaction.followup.send(f"Please choose a **category** from: {', '.join(ALLOWED_CATEGORIES)}", ephemeral=True)
        category_msg = await self.bot.wait_for('message', check=check)
        category = category_msg.content
        
        # Validate category
        if category not in ALLOWED_CATEGORIES:
            await interaction.followup.send(f"❌ Invalid category. Please choose a valid category from: {', '.join(ALLOWED_CATEGORIES)}", ephemeral=True)
            return
        
        # Ask for subcategory
        await interaction.followup.send(f"Please choose a **subcategory** for {category}:", ephemeral=True)
        subcategory_msg = await self.bot.wait_for('message', check=check)
        subcategory = subcategory_msg.content
        
        # Validate subcategory
        if subcategory not in CATEGORY_SUBCATEGORIES.get(category, []):
            await interaction.followup.send(f"❌ Invalid subcategory for {category}. Please choose a valid subcategory.", ephemeral=True)
            return
        
        # Ask for language
        await interaction.followup.send(f"Please enter the **language code** (e.g., 'en', 'fr'): {', '.join(ALLOWED_LANGUAGES)}", ephemeral=True)
        language_msg = await self.bot.wait_for('message', check=check)
        language = language_msg.content
        
        # Validate language
        if language not in ALLOWED_LANGUAGES:
            await interaction.followup.send(f"❌ Invalid language code. Choose from: {', '.join(ALLOWED_LANGUAGES)}", ephemeral=True)
            return
        
        # Save the metadata
        data = {
            "title": title,
            "author": author,
            "category": category,
            "subcategory": subcategory,
            "language": language,
            "file_hash": file_info["file_hash"],
            "message_id": file_info["message_id"],
            "channel_id": file_info["channel_id"],
            "user_id": file_info["user_id"],
            "username": file_info["username"]
        }
        
        insert_pdf(data)
        
        # Send confirmation
        embed = Embed(
            title="✅ PDF Added Successfully",
            description=f"**{data['title']}** by *{data['author']}*",
            color=discord.Color.green()
        )
        embed.add_field(name="Category", value=f"{data['category']} > {data['subcategory']}", inline=True)
        embed.add_field(name="Language", value=data['language'], inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # React to the original message
        try:
            channel = interaction.client.get_channel(file_info["channel_id"])
            message = await channel.fetch_message(file_info["message_id"])
            await message.add_reaction("✅")
        except:
            pass

async def setup(bot):
    await bot.add_cog(PDFUpload(bot))
