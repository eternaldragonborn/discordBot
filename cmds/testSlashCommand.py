import discord
from discord.ext import commands
from core.classes import Cog_Ext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import cog_ext, SlashContext, error

guildID = [719132687897591808]

class slashCommands(Cog_Ext):

  @cog_ext.cog_slash(guild_ids=guildID, name="test", description="This is just a test command, nothing more.")
  async def test(self, ctx):
    await ctx.send(content="Hello World!")

  @cog_ext.cog_slash(name='option', description='僅供測試', guild_ids=guildID, 
                    options=[create_option(
                      name='opt',
                      description='測試參數',
                      option_type=4,
                      required=True,
                      choices=[
                        create_choice(0, "零"),
                        create_choice(1, "一")
                      ]),
                      create_option(name='test', description='test', option_type=3, required=True)
                    ])
  async def optionTest(self, ctx, opt, test):
    await ctx.send(f"參數：{opt}\n類別：{type(opt)}", hidden=True)

  @cog_ext.cog_subcommand(base="group", name="say", guild_ids=guildID)
  async def group_say(self, ctx: SlashContext, text: str):
    await ctx.send(content=text)
  
  @commands.Cog.listener()
  async def on_slash_command_error(self, ctx, ex):
    if isinstance(ex, error.IncorrectFormat):
      await ctx.send("斜線指令格式錯誤，已進行紀錄", hidden=True)
    elif isinstance(ex, error.DuplicateCommand):
      await ctx.send("指令重複，已進行紀錄", hidden=True)
    elif isinstance(ex, error.IncorrectType):
      await ctx.send("輸入的參數類型錯誤", hidden=True)
    else:
      await ctx.send("發生例外錯誤，已進行紀錄", hidden=True)
    #await self.bot.get_channel(812628283631206431).send(f"指令：{ctx.message.content}(by {ctx.author.mention})\n錯誤：{error}")

def setup(bot):
  bot.add_cog(slashCommands(bot))