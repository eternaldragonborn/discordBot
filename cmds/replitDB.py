from core.classes import Cog_Ext
import discord
from discord.ext import commands
from replit import db

class replDB(Cog_Ext):

  @commands.command(hidden = True)
  async def setdata(self, ctx, key, value):
    if await self.bot.is_owner(ctx.author):
      db[key] = value
    await ctx.message.delete()

  @commands.command(hidden = True)
  async def getdata(self, ctx, key):
    if await self.bot.is_owner(ctx.author):
      await ctx.send(db[key])
    await ctx.message.delete()

def setup(bot):
  bot.add_cog(replDB(bot))