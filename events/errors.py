import discord
from discord.ext import commands
from core.classes import Cog_Ext
from games.an_jia import An_Jia

class Errors(Cog_Ext):

  @An_Jia.start_An_Jia.error
  async def start_An_Jia_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      await ctx.send("參數錯誤，指令用法：`+aj_s 項目 方法(0:骰子，1:硬幣，2:四色籤) 數量(項目為骰子時代表n面數)`\n所有參數皆為選填，但參數需照順序，例:要指定方法則須輸入項目", delete_after = 7)

  async def default_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send("缺少必要參數，請確認指令使用方法", delete_after = 5)
    elif isinstance(error, commands.BadArgument):
      await ctx.send("參數類別轉換錯誤，請確認是否輸入正確", delete_after = 5)
    else:
      await ctx.send("發生例外錯誤", delete_after = 5)

def setup(bot):
  bot.add_cog(Errors(bot))