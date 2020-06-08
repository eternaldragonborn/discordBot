import json
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='+')

with open("setting.json", "r", encoding= "utf8") as jsettings:
    setting = json.load(jsettings)

@bot.event
async def on_ready():
    print("Bot is online")

@bot.command()
async def load(ctx, folder, extension):
    if ctx.author == bot.get_user(setting["authorId"]):
        try:
            bot.load_extension(f"{folder}.{extension}")
        except:
            await ctx.send("Something went wrong.", delete_after = 3)
        else:
            await ctx.send(f"**{extension}** load successful.", delete_after = 3)
    else:
        await ctx.send("請不要冒充作者", delete_after= 3)
    await ctx.message.delete()

@bot.command()
async def unload(ctx, folder, extension):
    if ctx.author == bot.get_user(setting["authorId"]):
        try:
            bot.unload_extension(f"{folder}.{extension}")
        except:
            await ctx.send("Something went wrong.", delete_after = 3)
        else:
            await ctx.send(f"**{extension}** unload successful.", delete_after = 3)
    else:
        await ctx.send("請不要冒充作者", delete_after= 3)
    await ctx.message.delete()

@bot.command()
async def reload(ctx, folder, extension):
    if ctx.author == bot.get_user(setting["authorId"]):
        try:
            bot.reload_extension(f"{folder}.{extension}")
        except:
            await ctx.send("Something went wrong.", delete_after = 3)
        else:
            await ctx.send(f"**{extension}** reload successful.", delete_after = 3)
    else:
        await ctx.send("請不要冒充作者", delete_after= 3)
    await ctx.message.delete()

'''@bot.command()
async def printId(ctx):
    await ctx.send(ctx.author.id, delete_after = 10)
    #await ctx.send(setting["authorId"])
    #await ctx.send(type(setting["authorId"]))
    await ctx.message.delete()'''

bot.run(setting["token"])