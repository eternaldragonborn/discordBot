import discord
from discord.ext import commands
from core.classes import Cog_Ext

class CLEAN(Cog_Ext):
  @commands.command()
  async def clean(self, ctx, limit :int =999, target :int =719120395571298336):
    def judge(msg :discord.Message) -> bool:
      return msg.author.id == target
    if await self.bot.is_owner(ctx.author) or target == self.bot.id:
      await ctx.message.delete()
      count = await ctx.channel.purge(check = judge, limit = limit)
      await ctx.send(f"清除了 {len(count)} 條訊息", delete_after = 5)
    else:
      await ctx.send("You don't have permission or target is not a user.", delete_after = 3)
      await ctx.message.delete()

  @commands.command()
  async def clean_channel(self, ctx, channel :int, n :int =None):
    if await self.bot.is_owner(ctx.author) and channel == ctx.channel.id:
      count = len(await ctx.channel.purge(limit = n))
      await ctx.send(f"清除了 {len(count)} 條訊息", delete_after = 5)
    else:
      await ctx.send("You don't have permission or you are not in the target channel.", delete_after = 3)
      await ctx.message.delete()

  @commands.command()
  async def test(self, ctx, times :int=1):
    if await self.bot.is_owner(ctx.author):
      for i in range(times):
        await ctx.send("This is for test.")
      '''if msg == self.bot.get_user(authorId).mention:
        await ctx.send("y")'''
    await ctx.message.delete()

def setup(bot):
  bot.add_cog(CLEAN(bot))