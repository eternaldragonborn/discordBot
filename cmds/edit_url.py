import discord
from discord.ext import commands
import wrFiles
from core.classes import Cog_Ext

urls = wrFiles.readFile("others")
authorId = wrFiles.readFile("setting")["authorId"]

class EDIT_URL(Cog_Ext):
  @commands.command()
  async def add_url(self, cxt, item, url):
    if cxt.author.id == authorId:
      if item in urls.keys():
        try:
          urls[item].append(url)
        except:
          await cxt.send("新增失敗", delete_after = 3)
        else:
          await cxt.send("新增完畢", delete_after = 3)
      else:
        try:
          urls[item] = []
          urls[item].append(url)
        except:
          await cxt.send("新增失敗", delete_after = 3)
        else:
          await cxt.send("新增完畢", delete_after = 3)
      wrFiles.writeFile("others", urls)
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
          wrFiles.writeFile("others", urls)
      else:
        try:
          urls[item].remove(url)
        except:
          await cxt.send("刪除失敗", delete_after = 3)
        else:
          await cxt.send("刪除成功", delete_after = 3)
          wrFiles.writeFile("others", urls)
    await cxt.message.delete()

def setup(bot):
  bot.add_cog(EDIT_URL(bot))