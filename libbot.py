


# --- CONFIG ---
PDF_CHANNEL_ID = 1362503684117762108  # Replace with your target channel ID

from keep_alive import keep_alive
import discord
import asyncio
import sqlite3
import hashlib
import json
import re
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
current_time = datetime.utcnow().isoformat()

keep_alive()
# --- BOT SETUP ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def sync(ctx):
    """Sync slash commands to the server"""
    await bot.tree.sync()
    await ctx.send("Slash commands synced.")

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("pdf_catalogue.db")
cursor = conn.cursor()

ALLOWED_CATEGORIES = [
    "Philosophy", "Literature", "Math", "Science", "Traditional Islamic Studies", 
    "Politics", "Natural Sciences", "Computer Science", "Engineering", "History", "Art",
    "Western Islamic Studies"
]

# Update the category descriptions
CATEGORY_DESCRIPTIONS = {
    "Philosophy": "Texts dealing with philosophical concepts, thinkers, or traditions.",
    "Literature": "Novels, poetry, plays, and literary criticism.",
    "Math": "Mathematical theory, problem solving, or education.",
    "Science": "Scientific research or popular science works across all disciplines.",
    "Traditional Islamic Studies": "Books related to Islamic theology, law, history, and spirituality.",
    "Politics": "Political theory, commentary, and historical documents.",
    "Western Islamic Studies": "Islamic studies from Western academic perspectives.",
    "Natural Sciences": "Books related to biology, chemistry, physics, earth sciences, etc.",
    "Computer Science": "Texts related to programming, algorithms, data structures, and computing theory.",
    "Engineering": "Books related to various fields of engineering, including civil, electrical, mechanical, etc.",
    "History": "Historical accounts, events, and analysis from any time period.",
    "Art": "Books on visual arts, literature, music, and more."
}

# Update the category emojis
CATEGORY_EMOJIS = {
    "Philosophy": "🧠",
    "Literature": "📚",
    "Math": "➗",
    "Science": "🔬",
    "Traditional Islamic Studies": "☪️",
    "Politics": "⚖️",
    "Western Islamic Studies": "🤓",
    "Natural Sciences": "🌿",
    "Computer Science": "💻",
    "Engineering": "🛠️",
    "History": "📜",
    "Art": "🎨"
}

ALLOWED_LANGUAGES = ["en", "fr", "ar", "tr", "pr", "ur", "de"]

CATEGORY_SUBCATEGORIES = {
    "Philosophy": [
        "Greek Philosophy",
        "Islamic Philosophy (Falsafa)",
        "Medieval Christian & Jewish Thought",
        "Enlightenment & Rationalism",
        "German Idealism",
        "Postmodernism",
        "Critical Theory",
        "Phenomenology & Existentialism",
        "Logic & Epistemology",
        "Metaphysics",
        "Philosophy of Language",
        "Philosophy of Science",
        "Political Philosophy"
    ],
    "Literature": [
        "Classical Literature",
        "Modern Literature",
        "Poetry",
        "Drama",
        "Literary Criticism",
        "Fiction"
    ],
    "Math": [
        "Algebra",
        "Calculus",
        "Geometry",
        "Statistics",
        "Linear Algebra",
        "Number Theory",
        "Discrete Mathematics"
    ],
    "Science": [
        "Physics",
        "Chemistry",
        "Biology",
        "Astronomy",
        "Earth Sciences",
        "Environmental Science"
    ],
    "Traditional Islamic Studies": [
        "Islamic Theology",
        "Islamic History",
        "Islamic Law",
        "Islamic Mysticism (Sufism)",
        "Islamic Philosophy",
        "Quranic Studies"
    ],
    "Politics": [
        "Political Theory",
        "Political Economy",
        "Political Philosophy",
        "Public Policy",
        "International Relations"
    ],
    "Western Islamic Studies": [
        "Academic Studies",
        "Historical Analysis",
        "Contemporary Studies",
        "Orientalist Works",
        "Critical Analysis"
    ],
    "Natural Sciences": [
        "Physics",
        "Chemistry",
        "Biology",
        "Earth Sciences",
        "Environmental Science"
    ],
    "Computer Science": [
        "Programming",
        "Algorithms",
        "Data Structures",
        "Machine Learning",
        "Artificial Intelligence",
        "Cybersecurity"
    ],
    "Engineering": [
        "Mechanical Engineering",
        "Electrical Engineering",
        "Civil Engineering",
        "Software Engineering",
        "Aerospace Engineering"
    ],
    "History": [
        "Ancient History",
        "Medieval History",
        "Modern History",
        "Contemporary History",
        "History of Civilizations"
    ],
    "Art": [
        "Visual Arts",
        "Music",
        "Literary Arts",
        "Performance Arts",
        "Art History"
    ]
}


# Database update to store the subcategory
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS pdfs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        category TEXT,
        subcategory TEXT,  -- New column for subcategories
        language TEXT,
        file_hash TEXT,
        date_added TEXT,
        message_id INTEGER,
        channel_id INTEGER,
        user_id INTEGER,
        username TEXT
    )
''')

# Commit changes and close the connection
conn.commit()
try:
    cursor.execute('ALTER TABLE pdfs ADD COLUMN subcategory TEXT')
    conn.commit()
    print("Added subcategory column to existing database")
except sqlite3.OperationalError as e:
    # Column might already exist or there's another issue
    if "duplicate column name" not in str(e):
        print(f"Note about database: {e}")

async def get_file_hash(attachment):
    """Generate MD5 hash of file"""
    file = await attachment.read()
    return hashlib.md5(file).hexdigest()

async def delete_after_delay(message, delay=180):
    """Delete a message after specified delay"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass  # Message may already be deleted

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

class SubcategorySelect(discord.ui.Select):
    def __init__(self, subcategories):
        options = [discord.SelectOption(label=subcat, value=subcat) for subcat in subcategories]
        super().__init__(placeholder="Choose a subcategory...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_subcategory = self.values[0]
        await interaction.response.send_message(f"You selected the subcategory: **{self.values[0]}**", ephemeral=True)
        self.view.stop()

class SubcategoryView(discord.ui.View):
    def __init__(self, subcategories):
        super().__init__(timeout=180)
        self.selected_subcategory = None
        self.add_item(SubcategorySelect(subcategories))

@bot.event
async def on_message(message):
    """Event triggered when a message is sent"""
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.channel.id == PDF_CHANNEL_ID and message.attachments:
        pdf = next((a for a in message.attachments if a.filename.endswith('.pdf')), None)
        if pdf:
            file_hash = await get_file_hash(pdf)
            cursor.execute("SELECT 1 FROM pdfs WHERE file_hash = ?", (file_hash,))
            if cursor.fetchone():
                await message.delete()
                await message.author.send("This PDF has already been uploaded.")
                return

            msg = await message.reply("Please select the appropriate category:")
            for cat in ALLOWED_CATEGORIES:
                await msg.add_reaction(CATEGORY_EMOJIS[cat])

            # Start timeout for category selection
            bot.loop.create_task(delete_after_delay(msg))

            def check(reaction, user):
                return (
                    user.id == message.author.id and
                    str(reaction.emoji) in CATEGORY_EMOJIS.values() and
                    reaction.message.id == msg.id
                )

            try:
                reaction, _ = await bot.wait_for("reaction_add", timeout=180.0, check=check)
                category = [k for k, v in CATEGORY_EMOJIS.items() if v == str(reaction.emoji)][0]
            except asyncio.TimeoutError:
                await message.delete()
                await msg.delete()
                return

            # Get subcategory using the dropdown
            subcategories = CATEGORY_SUBCATEGORIES.get(category, [])
            subcategory_view = SubcategoryView(subcategories)
            subcat_msg = await msg.reply(f"Please select the appropriate subcategory from **{category}**:")
            await subcat_msg.edit(view=subcategory_view)
            
            # Wait for subcategory selection
            await subcategory_view.wait()
            subcategory = subcategory_view.selected_subcategory
            
            if not subcategory:
                await message.delete()
                await msg.delete()
                await subcat_msg.delete()
                return

            # Now ask for language
            lang_prompt = await msg.reply("What is the language? (en, fr, ar, tr, pr, ur, de)\n*This message will self-destruct in 3 minutes if no response*")
            bot.loop.create_task(delete_after_delay(lang_prompt))

            def lang_check(m):
                return m.author.id == message.author.id and m.channel.id == message.channel.id and m.content.lower() in ALLOWED_LANGUAGES

            try:
                lang_msg = await bot.wait_for("message", timeout=180.0, check=lang_check)
                language = lang_msg.content.lower()
                await lang_msg.delete()  # Delete user's response to keep channel clean
            except asyncio.TimeoutError:
                await message.delete()
                await msg.delete()
                await subcat_msg.delete()
                await lang_prompt.delete()
                return

            title_prompt = await msg.reply("Please provide the title of the PDF:\n*This message will self-destruct in 3 minutes if no response*")
            bot.loop.create_task(delete_after_delay(title_prompt))

            def title_check(m):
                return m.author.id == message.author.id and m.channel.id == message.channel.id

            try:
                title_msg = await bot.wait_for("message", timeout=180.0, check=title_check)
                title = title_msg.content
                await title_msg.delete()  # Delete user's response to keep channel clean
            except asyncio.TimeoutError:
                await message.delete()
                await msg.delete()
                await subcat_msg.delete()
                await lang_prompt.delete()
                await title_prompt.delete()
                return

            author_prompt = await msg.reply("Who is the author?\n*This message will self-destruct in 3 minutes if no response*")
            bot.loop.create_task(delete_after_delay(author_prompt))

            try:
                author_msg = await bot.wait_for("message", timeout=180.0, check=title_check)
                author = author_msg.content
                await author_msg.delete()  # Delete user's response to keep channel clean
            except asyncio.TimeoutError:
                await message.delete()
                await msg.delete()
                await subcat_msg.delete()
                await lang_prompt.delete()
                await title_prompt.delete()
                await author_prompt.delete()
                return

            # Store information in database
            cursor.execute(
                "INSERT INTO pdfs (title, author, category, subcategory, language, file_hash, date_added, message_id, channel_id, user_id, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (title, author, category, subcategory, language, file_hash, datetime.utcnow().isoformat(), 
                message.id, message.channel.id, message.author.id, str(message.author))
            )
            conn.commit()

            confirmation = await msg.reply(f"✅ Stored: **{title}** by *{author}* in **{category}** > **{subcategory}** ({language})")

            # Automatically delete all the prompts after a success
            await asyncio.sleep(10)  # Show confirmation for 10 seconds
            for prompt in [msg, subcat_msg, lang_prompt, title_prompt, author_prompt, confirmation]:
                try:
                    await prompt.delete()
                except:
                    pass

@bot.command()
async def explain_category(ctx, category_name: str):
    """Explains a specific category in detail."""
    # Check if the category exists
    if category_name in CATEGORY_DESCRIPTIONS:
        explanation = CATEGORY_DESCRIPTIONS[category_name]
        await ctx.send(f"**{category_name}**: {explanation}")
    else:
        await ctx.send(f"Sorry, I don't have an explanation for **{category_name}**.")

@bot.tree.command(name="searchpdf", description="Search PDFs naturally")
@app_commands.describe(query="Ask naturally like 'Philosophy books in English' or 'Math by John'...")
async def searchpdf(interaction: discord.Interaction, query: str):
    """Search PDFs using natural language queries"""
    await interaction.response.defer(ephemeral=True)
    
    query_lower = query.lower()
    clauses = []
    values = []

    # Search for categories in the query
    for cat in ALLOWED_CATEGORIES:
        if cat.lower() in query_lower:
            clauses.append("category LIKE ?")
            values.append(f"%{cat}%")

    # Search for languages in the query
    for lang in ALLOWED_LANGUAGES:
        if lang in query_lower:
            clauses.append("language LIKE ?")
            values.append(f"%{lang}%")

    # Search for author in the query (e.g., "by John")
    match_author = re.search(r"by ([a-zA-Z\s]+)", query)
    if match_author:
        author = match_author.group(1).strip()
        clauses.append("author LIKE ?")
        values.append(f"%{author}%")

    # Search for title in the query (e.g., "called The Theory of Everything")
    match_title = re.search(r"called ([a-zA-Z\s]+)", query)
    if match_title:
        title = match_title.group(1).strip()
        clauses.append("title LIKE ?")
        values.append(f"%{title}%")

    # If no criteria were found, perform a more general search on title or author
    if not clauses:
        clauses.append("title LIKE ? OR author LIKE ?")
        values.extend([f"%{query}%", f"%{query}%"])

    # Build query string
    query_str = " OR ".join(clauses)

    # Use your existing database structure
    cursor.execute(f"SELECT title, author, category, subcategory, language, channel_id, message_id, username FROM pdfs WHERE {query_str}", tuple(values))
    results = cursor.fetchall()

    # If no results are found, notify the user
    if not results:
        await interaction.followup.send("No matches found.", ephemeral=True)
        return

    # Sort results by relevance (basic implementation)
    def calculate_relevance(result):
        score = 0
        title, author, category, subcategory, language = result[0].lower(), result[1].lower(), result[2].lower(), result[3].lower() if result[3] else "", result[4].lower()
        
        # Check individual keywords
        keywords = query_lower.split()
        for keyword in keywords:
            if keyword in title:
                score += 3
            if keyword in author:
                score += 2
            if keyword in category:
                score += 1
            if keyword in subcategory:
                score += 1
            if keyword in language:
                score += 1
        
        return score

    sorted_results = sorted(results, key=calculate_relevance, reverse=True)
    
    # Create paginated results (5 per page)
    pages = [sorted_results[i:i+5] for i in range(0, min(len(sorted_results), 20), 5)]
    current_page = 0
    total_pages = len(pages)
    total_results = len(sorted_results)
    
    # Create an embed for the first page
    async def create_embed(page_num):
        embed = discord.Embed(
            title=f"PDF Search Results for: '{query}'",
            description=f"Found approximately {total_results} matches. Showing page {page_num+1}/{total_pages}",
            color=discord.Color.blue()
        )
        
        for i, (title, author, category, subcategory, language, channel_id, message_id, username) in enumerate(pages[page_num], 1):
            link = f"https://discord.com/channels/{interaction.guild.id}/{channel_id}/{message_id}"
            subcat_text = f" > {subcategory}" if subcategory else ""
            embed.add_field(
                name=f"{i}. {title} by {author}",
                value=f"Category: `{category}{subcat_text}` | Language: `{language}`\nAdded by: {username} | [Jump to PDF]({link})",
                inline=False
            )
            
        embed.set_footer(text="Use the buttons below to navigate results")
        return embed
    
    # Create action row with buttons for navigation
    class PdfNavigationView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)  # 3 minutes timeout
            
        @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.gray, disabled=(total_pages <= 1))
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal current_page
            current_page = max(0, current_page - 1)
            await interaction.response.edit_message(embed=await create_embed(current_page), view=self)
            
        @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.gray, disabled=(total_pages <= 1))
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal current_page
            current_page = min(total_pages - 1, current_page + 1)
            await interaction.response.edit_message(embed=await create_embed(current_page), view=self)
            
        @discord.ui.select(
            placeholder="Select to jump to PDF...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=f"{i+1}. {result[0][:40]}", 
                    description=f"By {result[1][:30]} - {result[2]}",
                    value=str(i)
                )
                for i, result in enumerate(sorted_results[:min(len(sorted_results), 20)])
            ]
        )
        async def select_pdf(self, interaction: discord.Interaction, select: discord.ui.Select):
            selected_index = int(select.values[0])
            selected_result = sorted_results[selected_index]
            _, _, _, _, _, channel_id, message_id, _ = selected_result
            
            link = f"https://discord.com/channels/{interaction.guild.id}/{channel_id}/{message_id}"
            await interaction.response.send_message(f"Here's your selected PDF: [Jump to Message]({link})", ephemeral=True)
    
    # Send the initial response with the embed and buttons
    await interaction.followup.send(embed=await create_embed(current_page), view=PdfNavigationView(), ephemeral=True)

class PDFCatalogueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # 3 minute timeout
        self.add_item(self.PDFSelect())
    
    class PDFSelect(discord.ui.Select):
        def __init__(self):
            cursor.execute("SELECT title, author, category, subcategory, language, message_id, channel_id, username, date_added FROM pdfs ORDER BY date_added DESC LIMIT 20")
            results = cursor.fetchall()
            
            options = []
            for title, author, category, subcategory, language, message_id, channel_id, username, date_added in results:
                # Truncate title if too long
                display_title = (title[:35] + '...') if len(title) > 35 else title
                subcat_text = f" > {subcategory}" if subcategory else ""
                options.append(
                    discord.SelectOption(
                        label=f"{display_title}", 
                        description=f"{author[:15]} - {category}{subcat_text} ({language})", 
                        value=f"{channel_id}-{message_id}"
                    )
                )
            
            # Ensure we have at least one option
            if not options:
                options = [discord.SelectOption(label="No PDFs found", value="none")]
                
            super().__init__(placeholder="Choose a PDF to view...", options=options, min_values=1, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            if self.values[0] == "none":
                await interaction.response.send_message("No PDFs available in the database.", ephemeral=True)
                return
                
            selected = self.values[0].split("-")
            channel_id, message_id = int(selected[0]), int(selected[1])
            
            # Get additional details for the selected PDF
            cursor.execute("SELECT title, author, subcategory, username, date_added FROM pdfs WHERE channel_id = ? AND message_id = ?", 
                          (channel_id, message_id))
            pdf_details = cursor.fetchone()
            
            if pdf_details:
                title, author, subcategory, username, date_added = pdf_details
                link = f"https://discord.com/channels/{interaction.guild.id}/{channel_id}/{message_id}"
                
                # Format the date nicely
                try:
                    date_obj = datetime.fromisoformat(date_added)
                    formatted_date = date_obj.strftime("%B %d, %Y at %H:%M UTC")
                except:
                    formatted_date = date_added
                
                subcat_text = f"\nSubcategory: {subcategory}" if subcategory else ""
                await interaction.response.send_message(
                    f"**{title}** by *{author}*{subcat_text}\n"
                    f"Uploaded by: {username or 'Unknown'} on {formatted_date}\n"
                    f"[Jump to PDF]({link})", 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message("PDF details not found.", ephemeral=True)

@bot.tree.command(name="catalog", description="Browse the PDF catalog")
async def catalog(interaction: discord.Interaction):
    """Command to view the PDF catalog"""
    # Get count of total PDFs
    cursor.execute("SELECT COUNT(*) FROM pdfs")
    total_count = cursor.fetchone()[0]
    
    view = PDFCatalogueView()
    
    await interaction.response.send_message(
        f"**📚 PDF Catalogue** - {total_count} total documents\n"
        f"Select a PDF from the list below to view details:\n"
        f"*This interface will expire after 3 minutes of inactivity*", 
        view=view
    )
    
    # Set up timeout behavior for the view
    original_message = await interaction.original_response()
    
    # Wait for the view to timeout
    await view.wait()
    
    # After timeout, delete the message
    try:
        await original_message.delete()
    except:
        pass

@bot.tree.command(name="topcollectors", description="See who has uploaded the most PDFs")
async def topcollectors(interaction: discord.Interaction):
    """Command to show top PDF contributors"""
    cursor.execute("""
        SELECT username, user_id, COUNT(*) as pdf_count 
        FROM pdfs 
        WHERE user_id IS NOT NULL
        GROUP BY user_id 
        ORDER BY pdf_count DESC 
        LIMIT 10
    """)
    results = cursor.fetchall()
    
    if not results:
        await interaction.response.send_message("No PDF uploads found.", ephemeral=True)
        return
        
    # Create a nice formatted leaderboard
    response = "# 📚 Top PDF Contributors 📚\n\n"
    
    for i, (username, user_id, count) in enumerate(results, 1):
        # Add emoji based on rank
        if i == 1:
            rank_emoji = "🥇"
        elif i == 2:
            rank_emoji = "🥈"
        elif i == 3:
            rank_emoji = "🥉"
        else:
            rank_emoji = "🏅"
            
        response += f"{rank_emoji} **{i}.** {username or f'User {user_id}'}: **{count}** PDF{'s' if count != 1 else ''}\n"
    
    # Get category distribution stats for the top collector
    if results:
        top_user = results[0][1]  # Get user_id of top contributor
        cursor.execute("""
            SELECT category, COUNT(*) as cat_count 
            FROM pdfs 
            WHERE user_id = ? 
            GROUP BY category 
            ORDER BY cat_count DESC
        """, (top_user,))
        category_stats = cursor.fetchall()
        
        if category_stats:
            top_username = results[0][0] or f'User {top_user}'
            response += f"\n**{top_username}'s Favorite Categories:**\n"
            for category, count in category_stats:
                category_emoji = CATEGORY_EMOJIS.get(category, "📄")
                response += f"{category_emoji} {category}: {count}\n"
    
    # Send response that will self-destruct
    await interaction.response.send_message(response)
    original_message = await interaction.original_response()
    
    # Delete after 3 minutes
    await asyncio.sleep(180)
    try:
        await original_message.delete()
    except:
        pass

@bot.tree.command(name="addcategory", description="Admin command to add a new category")
@app_commands.checks.has_permissions(administrator=True)
async def addcategory(interaction: discord.Interaction, category: str, emoji: str):
    """Admin command to add a new category"""
    if category in ALLOWED_CATEGORIES:
        await interaction.response.send_message("Category already exists.", ephemeral=True)
        return

    ALLOWED_CATEGORIES.append(category)
    CATEGORY_EMOJIS[category] = emoji
    CATEGORY_DESCRIPTIONS[category] = "No description provided yet."
    await interaction.response.send_message(f"Category **{category}** added with emoji {emoji}.")

@bot.tree.command(name="dumpjson", description="Admin command to export the database as JSON")
@app_commands.checks.has_permissions(administrator=True)
async def dumpjson(interaction: discord.Interaction):
    """Admin command to export database as JSON"""
    try:
        cursor.execute("SELECT title, author, category, subcategory, language, date_added, username FROM pdfs")
        data = cursor.fetchall()
        
        # Create proper JSON structure
        json_data = []
        for t, a, c, s, l, d, u in data:
            json_data.append({
                "title": t, 
                "author": a, 
                "category": c,
                "subcategory": s,
                "language": l, 
                "date_added": d, 
                "added_by": u or "Unknown"
            })
        
        # Convert to JSON string with proper encoding
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Split into chunks if needed (Discord message limit)
        if len(json_str) <= 1900:
            await interaction.response.send_message(f"```json\n{json_str}\n```", ephemeral=True)
        else:
            # Create a temporary file
            with open("pdf_export.json", "w", encoding="utf-8") as f:
                f.write(json_str)
            
            # Send as a file attachment
            file = discord.File("pdf_export.json")
            await interaction.response.send_message("Here's your JSON export:", file=file, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error exporting JSON: {str(e)}", ephemeral=True)

bot.run(TOKEN)
