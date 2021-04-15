#import json
import discord
from discord.ext import commands
from core.keep_alive import keep_alive
import os
from replit import db
import logging
from discord_slash import SlashCommand

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
error_log = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
error_log.setFormatter(formatter)
logger.addHandler(error_log)

bot = commands.Bot(command_prefix='+', owner_id = 384233645621248011)
bot.remove_command("help")
slash = SlashCommand(bot, override_type=True, sync_commands=True, sync_on_cog_reload=True)

'''with open("setting.json", "r", encoding= "utf8") as jsettings:
    setting = json.load(jsettings)'''
token = db['token']
#token = ""

@bot.event
async def on_ready():
    print("Bot is online")


def initialization(folder):
  for f in os.listdir(f"./{folder}"):
    if f.endswith(".py"):
      try:
        bot.load_extension(f"{folder}.{f[:-3]}")
      except Exception as e:
        print(e)
        print()
      else:
        print(f"{folder}.{f[:-3]} load success.")

initialization("cmds")

initialization("events")

initialization("games")

if __name__ == "__main__":
    keep_alive()
    try:
      bot.run(token)
    except Exception as e:
      print(e)