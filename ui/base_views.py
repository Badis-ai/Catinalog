import discord
from discord.ui import View

class BaseSubcategoryViewNav(View):
    def __init__(self, category, subcategories):
        super().__init__(timeout=180)
