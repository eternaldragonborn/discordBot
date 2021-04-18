import discord
from discord.ext import commands
from core.classes import Cog_Ext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import cog_ext, error
from core import slash_command

guildID = [719132687897591808]

class slashCommands(Cog_Ext):

  @cog_ext.cog_subcommand(base='command', name='get_list', description='取得斜線指令列表',
                          options=[
                            create_option(name='guildid', description='指定伺服器ID', option_type=3, required=False)
                          ])
  async def get_commands(self, ctx, guildid=None):
    r = slash_command.get_commands(guildid)
    await ctx.send(r, hidden=True)

  @cog_ext.cog_subcommand(base='command', name='edit', description='編輯斜線指令',
                          options=[
                            create_option(name='default_permission', description='預設權限', option_type=3, required=True,
                                          choices=[create_choice('True', '是'), create_choice('False', '否')]),
                            create_option(name='commandid', description='指令ID', option_type=3, required=True),
                            create_option(name='guildid', description='指定伺服器ID', option_type=3, required=False)
                          ])
  async def edit_command(self, ctx, default_permission, commandid, guildid=None):
    r = slash_command.edit_command(default_permission, commandid, guildid)
    await ctx.send(r, hidden=True)

  @cog_ext.cog_subcommand(base='command', subcommand_group='permission', name='get_list', description='取得斜線指令權限列表',
                          options=[
                            create_option(name='guildid', description='伺服器ID', option_type=3, required=True),
                            create_option(name='commandid', description='指令ID', option_type=3, required=False)
                          ])
  async def get_command_permission(self, ctx, guildid, commandid=None):
    r = slash_command.get_command_permissions(guildid, commandid)
    await ctx.send(r, hidden=True)

  @cog_ext.cog_subcommand(base='command', subcommand_group='permission', name='edit', description='修改斜線指令權限',
                          options=[
                            create_option(name='ids', description='使用者/身分組ID', option_type=3, required=True),
                            create_option(name='idtype', description='ID種類', option_type=4, required=True,
                                          choices=[create_choice(1, '身分組'), create_choice(2, '使用者')]),
                            create_option(name='permission', description='權限', option_type=3, required=True,
                                          choices=[create_choice('True', '是'), create_choice('False', '否')]),
                            create_option(name='guildid', description='伺服器ID', option_type=3, required=False),
                            create_option(name='commandid', description='指令ID', option_type=3, required=False)
                          ])
  async def edit_command_permission(self, ctx, ids, idtype:int, permission:bool, guildid=None, commandid=None):
    r = slash_command.edit_permission(ids, idtype, permission, guildid, commandid)
    await ctx.send(r, hidden=True)

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