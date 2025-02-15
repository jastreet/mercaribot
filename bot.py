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

# Per-channel search data: each channel id maps to a dict that holds search_terms and last_seen_items
channel_search_data = {}

# ----------------- DISCORD BOT COMMANDS -----------------

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    check_new_listings.start()

@bot.command(name='activate-channel')
async def activate_channel(ctx):
    if ctx.channel.id not in channel_search_data:
        channel_search_data[ctx.channel.id] = {"search_terms": [], "last_seen_items": {}}
        await ctx.send(f'Activated channel: {ctx.channel.name}')
    else:
        await ctx.send('This channel is already activated.')

@bot.command(name='add-search-term')
async def add_search_term(ctx, *, term):
    if ctx.channel.id not in channel_search_data:
        await ctx.send("Channel not activated. Use ~activate-channel to activate this channel.")
        return

    channel_data = channel_search_data[ctx.channel.id]
    if term not in channel_data["search_terms"]:
        channel_data["search_terms"].append(term)
        channel_data["last_seen_items"][term] = None  # Initialize tracking
        await ctx.send(f'Added search term: {term}')
    else:
        await ctx.send(f'Search term already exists: {term}')

@bot.command(name='remove-search-term')
async def remove_search_term(ctx, *, term):
    if ctx.channel.id not in channel_search_data:
        await ctx.send("Channel not activated. Use ~activate-channel to activate this channel.")
        return

    channel_data = channel_search_data[ctx.channel.id]
    if term in channel_data["search_terms"]:
        channel_data["search_terms"].remove(term)
        channel_data["last_seen_items"].pop(term, None)  # Remove tracking
        await ctx.send(f'Removed search term: {term}')
    else:
        await ctx.send(f'Search term not found: {term}')

@bot.command(name='list-search-terms')
async def list_search_terms(ctx):
    if ctx.channel.id not in channel_search_data:
        await ctx.send("Channel not activated. Use ~activate-channel to activate this channel.")
        return

    channel_data = channel_search_data[ctx.channel.id]
    if channel_data["search_terms"]:
        await ctx.send(f'Current search terms: {", ".join(channel_data["search_terms"])}')
    else:
        await ctx.send('No search terms found.')

# ----------------- CHECK FOR NEW LISTINGS -----------------

@tasks.loop(seconds=30)
async def check_new_listings():
    for channel_id, data in channel_search_data.items():
        channel = bot.get_channel(channel_id)
        if channel is None:
            continue  # Skip if channel is not found

        for term in data["search_terms"]:
            try:
                # Fetch most recent listings sorted by created time
                results = await mercari.search(term, sort_by=search.SearchRequestData.SortBy.SORT_CREATED_TIME)
                
                if results.items:
                    most_recent_item = results.items[0]

                    # Check if this is a new listing
                    if data["last_seen_items"].get(term) != most_recent_item.id_:
                        data["last_seen_items"][term] = most_recent_item.id_  # Update last seen listing
                        
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
                        logging.info(f"No new listings for '{term}' in channel {channel_id}. Latest ID: {most_recent_item.id_}")
            except Exception as e:
                logging.error(f"Error checking listings for '{term}' in channel {channel_id}: {e}")

# ----------------- RUN BOT -----------------

bot.run(TOKEN)