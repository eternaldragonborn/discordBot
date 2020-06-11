import discord
from discord.ext import commands
from core.classes import Cog_Ext
from core.wrFiles import readFile

authorId = readFile("setting")["authorId"]

class BASIC(Cog_Ext):
  @commands.command()
  async def load(self, ctx, folder, extension):
      if ctx.author == self.bot.get_user(authorId):
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
      if ctx.author == self.bot.get_user(authorId):
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
      if ctx.author == self.bot.get_user(authorId):
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
  
def setup(bot):
  bot.add_cog(BASIC(bot))