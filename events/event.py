from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random
from core.wrFiles import readFile
import re
import datetime

authorId = readFile("setting")["authorId"]
botId = readFile("setting")["botId"]

def choice_url(item):
  url = readFile("others")[item]
  return str(random.choices(list(url.keys()), weights = list(url.values()))).strip("[]'")

SAO = re.compile('星[\~` ]*[爆暴]|c8763|star(\s)*burst|(10|十)(\s)*(秒|sec)|((星光)|(西瓜)|(\N{WATERMELON})) *([流榴][槤蓮連]) *[擊雞機(\N{ROOSTER})]|桐([谷古][和核])?[人仁]|kirito|當我.?.?第[二2].|艾恩葛朗特')

class Events(Cog_Ext):
  @commands.Cog.listener()
  async def on_message(self, msg):
    if msg.author != self.bot.user and not msg.author.bot:
      if re.search(r'[rR啊阿ㄚ痾]{4,}', msg.content):
        await msg.channel.send(f"{msg.author.mention}\n{choice_url('rrr')}", delete_after=4)
      if "loading cat" in msg.content.lower():
        await msg.channel.send(choice_url("loadingCat"), delete_after=5)
      if SAO.search(msg.content.lower()) or SAO.search(msg.author.display_name) or "<:098:719589717955575879>" in msg.content:   #太快ㄌ
        await msg.add_reaction("\N{THUMBS DOWN SIGN}")
      if "虫合" in msg.content or "蛤" in msg.content:
        await msg.channel.send(choice_url("what"), delete_after=5)
      if re.search(r'[he]m{3,}|\N{THINKING FACE}', msg.content.lower()):
        await msg.channel.send(choice_url("emm"), delete_after = 10)
      if self.bot.user in msg.mentions:
        await msg.channel.send(f"{msg.author.mention} 吼嗚?", delete_after = 5)
      if msg.author == self.bot.get_user(294473515262803969) and (msg.attachments != [] or re.search('^<a?:.+>$', msg.content)):
        await msg.add_reaction("\N{THUMBS DOWN SIGN}")
        #await msg.delete()
      if "並沒有" in msg.content or "不要瞎掰" in msg.content:
        await msg.channel.send(choice_url("not"), delete_after = 10)
      if re.search(r"[^不]*好耶",msg.content):
        await msg.channel.send(choice_url("yeah"),delete_after = 10)
      if re.match(r"派[耶欸ㄟ]",msg.content):
        await msg.channel.send(choice_url("pie"), delete_after = 7)

  @commands.command()
  async def loading(self, ctx, delay_time: int = 5):
    await ctx.send(choice_url("loadingCat"), delete_after=delay_time)
    await ctx.message.delete(delay=delay_time)

  @commands.command()
  async def programming(self, ctx):
    await ctx.send(choice_url("programming"), delete_after = 4)
    await ctx.message.delete()

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    if message.guild.id == 669934356172636199 and not message.author.bot and not await self.bot.is_owner(message.author):
      await self.bot.get_channel(747054636778913853).send(f"`{(message.created_at + datetime.timedelta(hours = 8)).strftime('%Y-%m-%d %H:%M')}`\t{message.author.mention}：\n{message.content}")

  @commands.Cog.listener()
  async def on_guild_channel_pins_update(self, channel, last_pin):
    if channel.id == 747054636778913853:
      pins = await channel.pins()
      for pin in pins:
        await self.bot.get_channel(747825094046253126).send(pin.content)
        await pin.delete()


  '''@commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.CommandNotFound):
      pass'''


def setup(bot):
  bot.add_cog(Events(bot))
