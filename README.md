A Discord bot for managing and organizing PDF files shared in your server, with features for categorization, search, and preview generation.

## Features

- Auto-detection of PDF uploads in designated channels
- Interactive category-based browsing and searching of PDFs
- PDF previews with thumbnails and excerpts
- Search by natural language queries
- Admin commands for category management and data export

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with the following variables:
   ```
   DISCORD_TOKEN=your_bot_token_here
   PDF_CHANNEL_ID=channel_id_for_pdf_uploads
   ```
4. Run the bot: `python main.py`

## Commands

- `/catalog` - Browse the PDF collection through an interactive category tree
- `/recent_pdfs` - View the most recently added PDFs
- `/searchpdf` - Search PDFs with natural language queries
- `/preview` - Generate a preview of a PDF with thumbnail and excerpt

### Admin Commands

- `/addcategory` - Add a new category to the system
- `/topcollectors` - See users who have uploaded the most PDFs
- `/dumpjson` - Export the database to JSON format

## PDF Upload Process

1. Upload PDF files to the designated PDF channel
2. The bot will prompt for metadata (title, author, etc.)
3. Once metadata is provided, the file is cataloged and searchable

## Directory Structure

```
discord_pdf_bot/
├── main.py               # Initializes bot and loads commands
├── config.py             # Configuration constants
├── database.py           # Database connection and helpers
├── commands/             # Bot commands
│   ├── catalog.py        # Catalog browsing commands
│   ├── search.py         # Search functionality
│   ├── admin.py          # Admin commands
│   ├── pdf_management.py # PDF file management
│   └── pdf_upload.py     # PDF upload event handler
├── ui/                   # UI components
│   ├── base_views.py     # Base UI views
│   ├── buttons.py        # Button components
│   ├── selects.py        # Dropdown components
│   └── views.py          # UI views implementation
└── utils/                # Utility functions
    ├── file_utils.py     # File manipulation utilities
    └── pdf_utils.py      # PDF processing utilities
```
