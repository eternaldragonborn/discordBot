from core.classes import Cog_Ext
import discord, re
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

  @commands.command()
  async def getkeys(self, ctx):
    await ctx.message.delete()
    if await self.bot.is_owner(ctx.author):
      keys = db.keys()
      msg = ''
      for key in keys:
        if re.match(r'\d{18}', key):
          user = await self.bot.fetch_user(int(key))
          msg += f'{user.name}({key})\n'
        else:
          msg += f'{key}\n'
      await ctx.send(msg)

def setup(bot):
  bot.add_cog(replDB(bot))