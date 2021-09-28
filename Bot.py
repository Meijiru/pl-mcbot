import discord
import os
import sys
import asyncio
import logging

client = discord.Client()

from dotenv import load_dotenv
from discord.ext import tasks, commands

from connect_and_launch import get_status, get_number_of_players, \
                               get_ip, get_tps, get_queue
from connect_and_launch import connect_account, adblockBypass, refreshBrowser
from connect_and_launch import start_server, stop_server
from connect_and_launch import adblock
from embeds import server_info_embed, help_embed

from selenium.common.exceptions import ElementNotInteractableException

position = ""


# setup environment vars if .env doesn't exist
#if not os.path.exists(os.path.relpath(".env")):
#    launch_config()
#    sys.exit()

# load environment vars
#load_dotenv()
BOT_TOKEN = "ODkxMTk0NDUxMzc5MjI4Njky.YU6zgg.szVwrEUjG4yYHPxw9qnYDAP389Q"

# setup logger
logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s',
                    level=logging.INFO)

# bot settings
intents = discord.Intents.default()
allowed_mentions = discord.AllowedMentions(everyone=False, roles=False,
                                           users=True)
description = 'A simple tool to serve your own discord bot so you can ' \
              'manage an PloudOS server from discord.'
bot = discord.ext.commands.Bot(command_prefix='-', intents=intents,
                               allowed_mentions=allowed_mentions,
                               description=description,
                               case_insensitive=True,
                               help_command=None)


@bot.event
async def on_ready():
    text = "Logging into PloudOS..."
    await bot.change_presence(activity=discord.Game(name=text))

    connect_account()  # logs into PloudOS
    logging.info(f'The bot is logged in as: {bot.user}')
    await asyncio.sleep(3)
    serverStatus.start()  # starts the presence update loop

    # starts adblock loop if network adblock is on
    if adblock:
        adblockWall.start()

    resetBrowser.start()  # starts browser refresh loop


@bot.command()
async def launch(ctx):
    """ Launches the Minecraft Server"""
    server_status = get_status()

    if server_status == "Offline" or server_status == "Stopped":
        await ctx.send("Starting the server. \n      This might take a while...")
        await start_server()

        # if pinging a person, server will ping them when launching
        # else ping the the user who sent the command on launch
        if len(ctx.message.mentions) == 0:
            author = ctx.author
        else:
            author = ctx.message.mentions[0]

        # logs event to console
        logging.info(f'Server launched by: '
                     f'{author.name}#{author.discriminator}')

        # loops until server has started and pings person who launched
        while True:
            await asyncio.sleep(5)
            if get_status() == "Online":
                await ctx.send(f"{author.mention}, the server has started!")
                break

    elif server_status == "Online":
        await ctx.send("The server is already Online.")

    elif server_status == "Server will be prepaired" or server_status == "Server is starting" or server_status == "Queue":
        await ctx.send("The server is already starting...")

    elif server_status == "Stopping ..." or server_status == "Saving":
        await ctx.send("The server is stopping. Please wait.")

    else:
        text = "Server is currently under maintenance."
        await ctx.send(text)
        await start_server()


@bot.command()
async def status(ctx):
    """ Sends the servers status"""
    server_status = get_status()
    position = ""

    if server_status == "Queued":
        position = get_queue()
        await ctx.send(f"The server is Queued {position}")
    else:
        await ctx.send(f"The server is {get_status()}")


#@bot.command()
#async def players(ctx):
#    """ Sends the amount of players online."""
#    await ctx.send(f"There are {get_number_of_players()} players online.")


@bot.command()
async def info(ctx):
    await ctx.send(embed=server_info_embed())



@bot.command()
async def help(ctx):
    """ Help Command"""
    await ctx.send(embed=help_embed())


@tasks.loop(seconds=5.0)
async def serverStatus():
    server_status = get_status()
    position = ""
    if server_status == "Online":
        text = f"{server_status} | " \
               f"{get_ip()}"
    elif server_status == "Queued":
        position = get_queue()
        text = f"Queued {position} | " \
               f"{get_ip()}"
    elif server_status == None:
        text = f"Maintenance | " \
               f"{get_ip()}"
    else:
        text = f"{server_status} | " \
               f"{get_ip()}"
    activity = discord.Activity(type=discord.ActivityType.watching, name=text)
    await bot.change_presence(activity=activity)


@tasks.loop(seconds=5.0)
async def adblockWall():
    try:
        adblockBypass()
    except ElementNotInteractableException:
        pass

@bot.command()
async def stop(ctx):
    server_status = get_status()

    if server_status != 'Stopped' and server_status != 'Saving' and \
            server_status != 'Offline' and server_status != 'Server is starting':
        
        if len(ctx.message.mentions) == 0:
            author = ctx.author
        else:
            author = ctx.message.mentions[0]

        if author.name == "NyceTurtle":
            await ctx.send("Stopping the server...")
            await stop_server()
            # logs event to console
            logging.info(f'Server stopped by: '
                        f'{ctx.author.name}#{ctx.author.discriminator}')
        else:
            await ctx.send(f"{author.mention}, You're not allowed to do that!")
        

    elif server_status == 'Server is starting':
        await ctx.send(f"The server is currently loading. "
                       f"Please try again later.")

    else:
        await ctx.send("The server is already Offline.")

@tasks.loop(hours=1.0)
async def resetBrowser():
    refreshBrowser()
    if adblock:
        adblockBypass()
    logging.info('Refreshed browser')


bot.run(BOT_TOKEN)
