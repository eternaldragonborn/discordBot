import json
import discord
from discord.ext import commands
from core.keep_alive import keep_alive
import os

bot = commands.Bot(command_prefix='+', owner_id = 384233645621248011)
bot.remove_command("help")

with open("setting.json", "r", encoding= "utf8") as jsettings:
    setting = json.load(jsettings)

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
    bot.run(setting["token"])