from core import CogInit, readFile
from discord.ext import commands
import random, re, discord
from events.errors import Errors

authorId = readFile("setting")["authorId"]
botId = readFile("setting")["botId"]

def choice_url(item):
  url = readFile("others")[item]
  return str(random.choices(list(url.keys()), weights = list(url.values()))).strip("[]'")

SAO = re.compile('星[\~` ]*[爆暴]|c8763|star(\s)*burst|(10|十)(\s)*(秒|sec)|((星光)|(西瓜)|(\N{WATERMELON})) *([流榴][槤蓮連]) *[擊雞機(\N{ROOSTER})]|[桐銅]([谷古鼓][和核])?[人仁]|kirito|當我.?.?第[二2].|艾恩葛朗特')

class Events(CogInit):
  @commands.Cog.listener()
  async def on_message(self, msg):
    if not msg.author.bot:
      if msg.guild.id == 663305265130504207:
        delete_time = None
      else:
        delete_time = 7
      if re.search(r'[rR啊阿ㄚ痾]{4,}', msg.content):
        await msg.channel.send(f"{msg.author.mention}\n{choice_url('rrr')}", delete_after=delete_time)
      if "loading cat" in msg.content.lower():
        await msg.channel.send(choice_url("loadingCat"), delete_after=delete_time)
      if SAO.search(msg.content.lower()) or SAO.search(msg.author.display_name) or "<:098:719589717955575879>" in msg.content:   #太快ㄌ
        await msg.add_reaction("\N{THUMBS DOWN SIGN}")
      if "虫合" in msg.content or "蛤" in msg.content:
        await msg.channel.send(choice_url("what"), delete_after=delete_time)
      if re.search(r'[he]m{3,}|\N{THINKING FACE}', msg.content.lower()):
        await msg.channel.send(choice_url("emm"), delete_after = delete_time)
      if self.bot.user in msg.mentions:
        reply = random.choices([f"{msg.author.mention} 吼嗚?", "嘎嘎嘎", "作者很懶，沒留下任何回覆。"], weights = [7,7,3])[0]
        await msg.reply(reply)
      if "並沒有" in msg.content or "不要瞎掰" in msg.content:
        await msg.channel.send(choice_url("not"), delete_after = delete_time)
      if re.search(r"[^不]*好耶",msg.content):
        await msg.channel.send(choice_url("yeah"),delete_after = delete_time)
      if re.match(r"派[耶欸ㄟ]",msg.content):
        await msg.channel.send(choice_url("pie"), delete_after = delete_time)
      if re.search(r'[打揍殺屠砍幹尻][\s\n\W]*[龍竜(多拉貢)]', msg.content) and not await self.bot.is_owner(msg.author):
        await msg.reply('<:092:819621685010366475>'*3)
      if re.search(r'([＼／\\\|/]\s?){3}|(上香)|(:021:)|(:034:)', msg.content):
        await msg.reply(choice_url('pray'))

  @commands.command()
  async def loading(self, ctx, delay_time: int = 5):
    await ctx.send(choice_url("loadingCat"), delete_after=delay_time)
    await ctx.message.delete(delay=delay_time)

  @commands.command()
  async def programming(self, ctx):
    await ctx.send(choice_url("programming"), delete_after = 7)
    await ctx.message.delete()

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    if isinstance(error, commands.CommandNotFound):
      pass
    else:
      try:
        await ctx.message.delete()
      except:
        pass
      error_command = f"{ctx.command}_error"
      if hasattr(Errors, error_command):
        error_cmd = getattr(Errors, error_command)
        await error_cmd(self, ctx, error)
      else:
        if not await self.bot.is_owner(ctx.author):
          await self.bot.get_channel(812628283631206431).send(f"指令：{ctx.message.content}(by {ctx.author.mention})\n錯誤：{error}")
        await Errors.default_error(self, ctx, error)


def setup(bot):
  bot.add_cog(Events(bot))
