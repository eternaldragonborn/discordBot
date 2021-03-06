import discord
from discord.ext import commands
from core.classes import Cog_Ext
from core.wrFiles import readFile
import datetime

authorId = readFile("setting")["authorId"]
botId = readFile("setting")["botId"]

class BASIC(Cog_Ext):
  @commands.command()
  async def load(self, ctx, folder, extension):
      #if ctx.author == self.bot.get_user(authorId):
      if await self.bot.is_owner(ctx.author):
          try:
              self.bot.load_extension(f"{folder}.{extension}")
          except Exception as e:
              await ctx.send(f"Something went wrong, exception:***{e}***", delete_after = 3)
              print(e)
              print()
          else:
              await ctx.send(f"> **{extension}** load successful.", delete_after = 3)
      else:
          await ctx.send("請不要冒充作者", delete_after= 3)
      await ctx.message.delete()

  @commands.command()
  async def unload(self, ctx, folder, extension):
      #if ctx.author == self.bot.get_user(authorId):
      if await self.bot.is_owner(ctx.author):
          try:
              self.bot.unload_extension(f"{folder}.{extension}")
          except Exception as e:
              await ctx.send(f"Something went wrong, exception:***{e}***", delete_after = 3)
              print(e)
              print()
          else:
              await ctx.send(f"> **{extension}** unload successful.", delete_after = 3)
      else:
          await ctx.send("請不要冒充作者", delete_after= 3)
      await ctx.message.delete()

  @commands.command()
  async def reload(self, ctx, folder, extension):
      #if ctx.author == self.bot.get_user(authorId):
      if await self.bot.is_owner(ctx.author):
          try:
              self.bot.reload_extension(f"{folder}.{extension}")
          except Exception as e:
              print(e)
              print()
              await ctx.send(f"Something went wrong, exception:***{e}***", delete_after = 7)
          else:
              await ctx.send(f"> **{extension}** reload successful.", delete_after = 3)
      else:
          await ctx.send("請不要冒充作者", delete_after= 3)
      await ctx.message.delete()
			
  @commands.command()
  async def help(self, ctx):
    embed=discord.Embed(title="指令列表", description = '<>內代表非必要，輸入時不必打括號，ex:+loading 10', color=0x3774d7)
    embed.set_author(name="DragonBot",icon_url="https://cdn.discordapp.com/app-icons/719120395571298336/e2ea7b8292b811643fa84dbc3161e1ed.png?size=128")
    embed.set_thumbnail(url="https://i.imgur.com/NM1YCnf.jpg")
    for Command, description in readFile("others")["help"].items():
      embed.add_field(name= Command, value= description, inline=False)
    embed.set_footer(text="就是一隻龍，毫無反應。")
    await ctx.send(embed = embed)
    await ctx.message.delete()
  
  @commands.command()
  async def nowtime(self, ctx):
    tz = datetime.timezone(datetime.timedelta(hours=8))
    await ctx.send(datetime.datetime.now(tz))
  
def setup(bot):
  bot.add_cog(BASIC(bot))