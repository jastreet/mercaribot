import discord
from discord.ext import commands, tasks
import asyncio
import os
import logging
from dotenv import load_dotenv
from mercapi import Mercapi
from mercapi.requests import search

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='~', intents=intents)

# Mercari API instance
mercari = Mercapi()

# Active channel and search terms
active_channel_id = None
search_terms = []
last_seen_items = {}  # Store the last seen item ID per search term

# ----------------- DISCORD BOT COMMANDS -----------------

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    check_new_listings.start()

@bot.command(name='activate-channel')
async def activate_channel(ctx):
    global active_channel_id
    active_channel_id = ctx.channel.id
    await ctx.send(f'Activated channel: {ctx.channel.name}')

@bot.command(name='add-search-term')
async def add_search_term(ctx, *, term):
    if term not in search_terms:
        search_terms.append(term)
        last_seen_items[term] = None  # Initialize tracking
        await ctx.send(f'Added search term: {term}')
    else:
        await ctx.send(f'Search term already exists: {term}')

@bot.command(name='remove-search-term')
async def remove_search_term(ctx, *, term):
    if term in search_terms:
        search_terms.remove(term)
        last_seen_items.pop(term, None)  # Remove tracking
        await ctx.send(f'Removed search term: {term}')
    else:
        await ctx.send(f'Search term not found: {term}')

@bot.command(name='list-search-terms')
async def list_search_terms(ctx):
    if search_terms:
        await ctx.send(f'Current search terms: {", ".join(search_terms)}')
    else:
        await ctx.send('No search terms found.')

# ----------------- CHECK FOR NEW LISTINGS -----------------

@tasks.loop(seconds=30)  # Check every 30 seconds
async def check_new_listings():
    if active_channel_id is None:
        return

    channel = bot.get_channel(active_channel_id)
    
    for term in search_terms:
        try:
            # Fetch most recent listings sorted by created time
            results = await mercari.search(term, sort_by=search.SearchRequestData.SortBy.SORT_CREATED_TIME)
            
            if results.items:
                most_recent_item = results.items[0]

                # Check if this is a new listing
                if last_seen_items.get(term) != most_recent_item.id_:
                    last_seen_items[term] = most_recent_item.id_  # Update last seen listing
                    
                    # Fetch full item details
                    full_item = await most_recent_item.full_item()

                    # Create embed message
                    embed = discord.Embed(
                        title="New Listing Found!",
                        description=(
                            f'**Search Term:** {term}\n'
                            f"**Name:** {most_recent_item.name}\n"
                            f"**Price:** {most_recent_item.price}¥\n"
                            f"**Created:** {full_item.created.strftime('%Y-%m-%d %H:%M:%S')}"
                        ),
                        url=f"https://www.mercari.com/jp/items/{most_recent_item.id_}",
                        color=discord.Color.blue()
                    )
                    if full_item.photos:
                        embed.set_thumbnail(url=full_item.photos[0])

                    await channel.send(embed=embed)
                else:
                    logging.info(f"No new listings for '{term}'. Latest ID: {most_recent_item.id_}")
                    
        except Exception as e:
            logging.error(f"Error checking listings for '{term}': {e}")

# ----------------- RUN BOT -----------------

bot.run(TOKEN)
