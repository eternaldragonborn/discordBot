import discord
from discord.ext import commands
from core.classes import Cog_Ext
from core.wrFiles import readFile
from discord_slash import cog_ext

authorId = readFile("setting")["authorId"]
botId = readFile("setting")["botId"]
guildID = [719132687897591808]

class BASIC(Cog_Ext):
  @cog_ext.cog_subcommand(base='extension')
  async def load(self, ctx, folder, extension):
      if await self.bot.is_owner(ctx.author):
          try:
              self.bot.load_extension(f"{folder}.{extension}")
          except Exception as e:
              await ctx.send(f"Something went wrong, exception:***{e}***", delete_after = 3)
              print(e)
              print()
          else:
              await ctx.send(f"> **{extension}** has been loaded.", delete_after = 3)
      else:
          await ctx.send("請不要冒充作者", delete_after= 3)

  @cog_ext.cog_subcommand(base='extension')
  async def unload(self, ctx, folder, extension):
      if await self.bot.is_owner(ctx.author):
          try:
              self.bot.unload_extension(f"{folder}.{extension}")
          except Exception as e:
              await ctx.send(f"Something went wrong, exception:***{e}***", delete_after = 3)
              print(e)
              print()
          else:
              await ctx.send(f"> **{extension}** has been unloaded.", delete_after = 3)
      else:
          await ctx.send("請不要冒充作者", delete_after= 3)

  @cog_ext.cog_subcommand(base='extension')
  async def reload(self, ctx, folder, extension):
      if await self.bot.is_owner(ctx.author):
          try:
              self.bot.reload_extension(f"{folder}.{extension}")
          except Exception as e:
              print(e)
              print()
              await ctx.send(f"Something went wrong, exception:***{e}***", delete_after = 7)
          else:
              await ctx.send(f"> **{extension}** has been reloaded.", delete_after = 3)
      else:
          await ctx.send("請不要冒充作者", delete_after= 3)
			
  @commands.command()
  async def help(self, ctx, command = ""):
    await ctx.message.delete()
    if not command:
      embed=discord.Embed(title="指令列表", description = '<>內代表非必要，輸入時不必打括號，ex:+loading 10', color=0x3774d7)
      embed.set_author(name="DragonBot",icon_url="https://cdn.discordapp.com/app-icons/719120395571298336/e2ea7b8292b811643fa84dbc3161e1ed.png?size=128")
      embed.set_thumbnail(url="https://i.imgur.com/NM1YCnf.jpg")
      for Command, description in readFile("others")["help"].items():
        embed.add_field(name= Command, value= description, inline=False)
      embed.set_footer(text="就是一隻龍，毫無反應。")
      await ctx.send(embed = embed)
      await ctx.message.delete()
    else:
      cmd = self.bot.get_command(command)
      if cmd == None: await ctx.send("查無此指令，請確認是否輸入正確", delete_after = 5)
      elif not cmd.help: await ctx.send("此指令尚未編寫help，有問題請洽宇", delete_after = 5)
      else: await ctx.send(f'指令中參數若有"<>"代表非必要，輸入時"<>"不需輸入\n```用法：{cmd.usage}\n說明:{cmd.help}```', delete_after = 15)
  
def setup(bot):
  bot.add_cog(BASIC(bot))