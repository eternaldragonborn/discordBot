import discord
from discord.ext import commands
from core.classes import Cog_Ext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import cog_ext, error

guildID = [719132687897591808]

class slashCommands(Cog_Ext):

  @commands.Cog.listener()
  async def on_slash_command_error(self, ctx, ex):
    if isinstance(ex, error.IncorrectFormat):
      await ctx.send("斜線指令格式錯誤，已進行紀錄", hidden=True)
    elif isinstance(ex, error.DuplicateCommand):
      await ctx.send("指令重複，已進行紀錄", hidden=True)
    elif isinstance(ex, error.IncorrectType):
      await ctx.send("輸入的參數類型錯誤", hidden=True)
    else:
      await ctx.send(f"發生例外錯誤 {ex}，已進行紀錄", hidden=True)
    await self.bot.get_channel(812628283631206431).send(f"指令：/{ctx.name}(id:{ctx.command_id}, by:{ctx.author.mention})\n錯誤：{error}")

  @commands.Cog.listener()
  async def on_slash_command(self, ctx):
    if not await self.bot.is_owner(ctx.author):
      msg = f'/{ctx.name}'
      if ctx.subcommand_name:
        msg += f' {ctx.subcommand_name} '
      if ctx.subcommand_group:
        msg += f' {ctx.subcommand_group} '
      for arg, value in ctx.kwargs.items():
        msg += f' `{arg}`:`{value}`'
      msg += f'\n(commandID:{ctx.command_id}, by:{ctx.author.mention})'
      await self.bot.get_channel(747054636778913853).send(msg)

def setup(bot):
  bot.add_cog(slashCommands(bot))