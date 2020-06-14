import discord
from discord.ext import commands
import core.wrFiles
from core.classes import Cog_Ext

urls = core.wrFiles.readFile("others")
authorId = core.wrFiles.readFile("setting")["authorId"]

class EDIT_URL(Cog_Ext):
  @commands.command()
  async def add_url(self, cxt, item, url, weight :int=1):
    if cxt.author.id == authorId:
      if item in urls.keys():
        if url in urls[item].keys():
          await cxt.send("此圖已在檔案中", delete_after = 3)
        else:
          try:
            newurl = {url : weight}
            urls[item].update(newurl)
          except:
            await cxt.send("新增失敗", delete_after = 3)
          else:
            await cxt.send("新增完畢", delete_after = 3)
      else:
        try:
          newitem = {item : {url : weight}}
          urls.update(newitem)
        except:
          await cxt.send("新增失敗", delete_after = 3)
        else:
          await cxt.send("新增完畢", delete_after = 3)
      core.wrFiles.writeFile("others", urls)
    await cxt.message.delete()

  @commands.command()
  async def del_url(self, cxt, item, url=""):
    if cxt.author.id == authorId:
      if url == "":
        try:
          del urls[item]
        except:
          await cxt.send("刪除失敗", delete_after = 3)
        else:
          await cxt.send("刪除成功", delete_after = 3)
          core.wrFiles.writeFile("others", urls)
      else:
        try:
          del urls[item][url]
        except:
          await cxt.send("刪除失敗", delete_after = 3)
        else:
          await cxt.send("刪除成功", delete_after = 3)
          core.wrFiles.writeFile("others", urls)
    await cxt.message.delete()

  @commands.command()
  async def edit_weight(self, ctx, item, url, weight :int):
    if ctx.author.id == authorId:
      try:
        urls[item][url] = weight
      except Exception as e:
        await ctx.send("更改失敗", delete_after = 3)
        print(e,"\n")
      else:
        await ctx.send("更改成功", delete_after = 3)
        core.wrFiles.writeFile("others", urls)
    await ctx.message.delete()
  


def setup(bot):
  bot.add_cog(EDIT_URL(bot))