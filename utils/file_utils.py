# utils/file_utils.py
import hashlib
import asyncio
import os

async def get_file_hash(attachment) -> str:
    """Generate an MD5 hash for a Discord attachment"""
    file = await attachment.read()
    return hashlib.md5(file).hexdigest()

async def delete_after_delay(message, delay=180):
    """Deletes a Discord message after a delay (in seconds)"""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass  # It's already gone
