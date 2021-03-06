import random
import datetime

import discord
from discord.ext import commands, tasks

from secret.constants import *

from utils.embed import CrajyEmbed

from internal.bot import CrajyBot
from internal.enumerations import Table, EmbedType


intents = discord.Intents.default()
intents.members = True 
intents.messages = True
bot = CrajyBot(command_prefix=commands.when_mentioned_or("."),
               activity=discord.Activity(type=discord.ActivityType.watching, name="thug_sgt"),
               intents=intents,
               owner_id=271586885346918400)

bot.task_loops = dict()    # add all task loops, across cogs to this.

last_4 = []                # List for stock loop correction

@bot.listen("on_message")
async def chat_money_tracker(message):
    if message.author.bot:
        return

    if message.channel.id in CHAT_MONEY_CHANNELS:
        bot.chat_money_cache[message.author.id] += 1

@tasks.loop(hours=3)
async def stock_price():
    message_channel = bot.get_channel(BOT_ANNOUNCE_CHANNEL)

    rand_sign = random.choice(["+","-"])
    pos = 0
    neg = 0
    if rand_sign == "+":
        rand_val = random.randint(1,6)
        emb_type = EmbedType.SUCCESS
    else:
        rand_val = -random.randint(1,6)
        emb_type = EmbedType.FAIL
    
    last_4.append(rand_val)
    if len(last_4) > 4:
        del last_4[0]
    
    for i in last_4:
        if i < 0:
            neg += 1
        else:
            pos += 1

    if pos >= random.randint(1,6):
        rand_val = -(rand_val)
        emb_type = EmbedType.FAIL
    elif neg >= random.randint(1,6):
        rand_val = -(rand_val)
        emb_type = EmbedType.SUCCESS
    
    new = await bot.db_pool.fetchval(f"UPDATE shop SET price=price + $1 WHERE item_name='stock' RETURNING price", rand_val)

    embed = CrajyEmbed(title="Stock Price Updated!", embed_type=emb_type)
    embed.description = f"New price: {new}"
    embed.quick_set_author(bot.user)
    await message_channel.send(embed=embed)

@stock_price.before_loop
async def stock_price_before():
    await bot.wait_until_ready()

@tasks.loop(hours=24)
async def birthday_loop():
    guild = bot.get_guild(GUILD_ID)
    wishchannel = guild.get_channel(GENERAL_CHAT)
    data = await bot.db_pool.fetch("SELECT user_id FROM user_details WHERE EXTRACT(day FROM bday)=EXTRACT(day FROM current_date) AND EXTRACT(month FROM bday)=EXTRACT(month FROM current_date)")

    for person in data:
        person_obj = discord.utils.get(guild.members, id=person['user_id'])
        embed = CrajyEmbed(title=f"Happy Birthday {person_obj.display_name}!", embed_type=EmbedType.SUCCESS)
        embed.quick_set_author(person_obj)
        await wishchannel.send(content="@here", embed=embed)

@birthday_loop.before_loop
async def birthdayloop_before():
    await bot.wait_until_ready()

bot.task_loops["stock"] = stock_price 
bot.task_loops["birthday"] = birthday_loop

if __name__ == "__main__":
    raise Exception("Use the manage.py interface to run the bot.")
