from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random
from core.wrFiles import readFile
import re

authorId = readFile("setting")["authorId"]
botId = readFile("setting")["botId"]

def choice_url(item):
  url = readFile("others")[item]
  return str(random.choices(list(url.keys()), weights = list(url.values()))).strip("[]'")

SAO = re.compile('星(爆|暴)|c8763|star(\s)?burst|(10|十)\s*(秒|sec)|(星光|西瓜)(流連|榴槤)(擊|雞|機)|桐(人|仁)|kirito')

class Events(Cog_Ext):
  @commands.Cog.listener()
  async def on_message(self, msg):
    if msg.author != self.bot.user:
      if re.search(r'[rR啊阿ㄚ痾]{4,}', msg.content):
        await msg.channel.send(f"{msg.author.mention}\n{choice_url('rrr')}", delete_after=4)
      elif "loading cat" in msg.content.lower():
        await msg.channel.send(choice_url("loadingCat"), delete_after=5)
      #elif re.search(r'星爆|星暴|c8763|star(\s)?burst|(10|十)[^:分月/\-\s\d\.]+(16|十六)[^秒]|(10|十)\s*秒', msg.content.lower()):
      elif SAO.search(msg.content.lower()):
        await msg.add_reaction("\N{THUMBS DOWN SIGN}")
      elif "虫合" in msg.content or "蛤" in msg.content:
        await msg.channel.send(choice_url("what"), delete_after=5)
      elif re.search(r'em{3,}|\N{THINKING FACE}', msg.content.lower()):
        await msg.channel.send(choice_url("emmm"), delete_after = 10)

  @commands.command()
  async def loading(self, ctx, delay_time: int = 5):
    await ctx.send(choice_url("loadingCat"), delete_after=delay_time)
    await ctx.message.delete(delay=delay_time)

  @commands.command()
  async def programming(self, ctx):
    await ctx.send(choice_url("programming"), delete_after = 4)
    await ctx.message.delete()

  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction, user):
    print(reaction)

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.CommandError):
      pass


def setup(bot):
  bot.add_cog(Events(bot))
