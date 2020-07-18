import datetime
from core.classes import Cog_Ext
import discord
from discord.ext import commands
from core.wrFiles import readFile, writeFile
import re
from redis import Redis, ConnectionPool

# {artists : {author : [subscriber, lastUpdate, mark]},
#  subscribers : {subscriber : [preview_url, download_url, artist...]}}
manager = [590430031281651722, 384233645621248011, 546614210243854337]

def mention_vaild(mention):
  if re.match('<@!?\d{18}>', mention):
    return True
  else:
    return False

setting = readFile("setting")["redis"]
host = setting["host"]
port = setting["port"]
password = setting["password"]
pool = ConnectionPool(host=host, port=port, password=password)

class SUBSCRIBE(Cog_Ext):

  async def print_overview(self, data):
    setting = readFile("setting")
    message = "訂閱總覽(如需更改請告知管理者，繪師名中的空格皆以_取代)\n> "
    for subscriber, content in data["subscribers"].items():
      message+=f"{subscriber}："
      if len(content[2:]) == 0:
        message += "\n"
      for artist in content[2:]:
        if artist != content[-1]:
          message+=f"`{artist}`{data['artists'][artist][2]}、"
        else:
          message+=f"`{artist}`{data['artists'][artist][2]}\n"
    if message == "":
      message = "` `"
    try:
      overview = await self.bot.get_channel(675956755112394753).fetch_message(setting["overview"])
    except:
      msg = await self.bot.get_channel(675956755112394753).send(message)
      await msg.pin()
      setting["overview"] = msg.id
      writeFile("setting", setting)
    else:
      await overview.edit(content = message)

  @commands.command(aliases = ["add_suber"])
  async def new_subscriber(self, ctx, subscriber, download_url, preview_url=None):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and mention_vaild(subscriber) and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 670517724350382082):
      data = readFile("subscribe&update")
      if subscriber in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 已在訂閱者名單", delete_after = 5)
      else:
        try:
          subscriberData = {subscriber : [preview_url, download_url]}
          data["subscribers"].update(subscriberData)
          await SUBSCRIBE.print_overview(self, data)
          writeFile("subscribe&update", data)
        except Exception as e:
          await ctx.send(f"新增錯誤， {e}", delete_after = 5)
          print(e)
        else:
          await ctx.send("訂閱者資料新增完畢", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此用戶", delete_after = 5)

  @commands.command(aliases = ["edit_suber"])
  async def edit_subscriber(self, ctx, subscriber, download_url, preview_url=""):
    global manager
    await ctx.message.delete()
    if mention_vaild(subscriber) and (ctx.author.id in manager or ctx.author.id == subscriber[2:-1]) and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 670517724350382082):
      data = readFile("subscribe&update")
      if subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內")
      else:
        try:
          data["subscribers"][subscriber][0] = preview_url
          data["subscribers"][subscriber][1] = download_url
          await SUBSCRIBE.print_overview(self, data)
        except Exception as e:
          await ctx.send(f"修改資料錯誤, {e}", delete_after = 5)
          print(e)
        else:
          await ctx.send("訂閱者資料更改完畢", delete_after = 5)
    await ctx.send("沒有權限或無此ID", delete_after = 5)
  
  @commands.command(aliases = ["sub"])
  async def subscribe(self, ctx, subscriber, artist, lastUpdate=None, *, mark=""):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and mention_vaild(subscriber) and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 675956755112394753):
      subscriber = subscriber.replace("!", "")
      data = readFile("subscribe&update")
      if artist in data["artists"].keys():
        await ctx.send(f"繪師 `{artist}` 已有訂閱紀錄", delete_after = 5)
      elif subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      else:
        if not lastUpdate:
          lastUpdate = (ctx.message.created_at + datetime.timedelta(hours= 8)).strftime("%m.%d")
        if mark:
          mark = f"({mark})"
        new_subscribe = {artist : [subscriber, lastUpdate, mark]}
        msg = await ctx.send(f"請確認 {subscriber} 訂閱 `{artist}`{mark}，最後更新於 {lastUpdate}")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{CROSS MARK}")
        def check(reaction, user):
          if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}" and reaction.message.id == msg.id and user == ctx.author:
            return True
          elif str(reaction.emoji) == "\N{CROSS MARK}" and reaction.message.id == msg.id and user == ctx.author:
            raise "order_cancel"
        try:
          await self.bot.wait_for("reaction_add", check = check)
        except:
          await ctx.send("新增資料取消", delete_after = 5)
        else:
          data["artists"].update(new_subscribe)
          data["subscribers"][subscriber].append(artist)
          await SUBSCRIBE.print_overview(self, data)
          try:
            writeFile("subscribe&update", data)
          except Exception as e:
            await ctx.send(f"新增錯誤， {e}", delete_after = 5)
            print(e)
          else:
            await ctx.send("新增完畢", delete_after = 5)
        finally:
          await msg.delete()
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)
  
  @commands.command(aliases = ["unsub"])
  async def unsubscribe(self, ctx, artist):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 675956755112394753):
      data = readFile("subscribe&update")
      if artist in data["artists"].keys():
        msg = await ctx.send(f"請確認 {data['artists'][artist][0]} 取消訂閱 `{artist}`")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{CROSS MARK}")
        def check(reaction, user):
            if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}" and reaction.message.id == msg.id and user == ctx.author:
              return True
            elif str(reaction.emoji) == "\N{CROSS MARK}" and reaction.message.id == msg.id and user == ctx.author:
              raise "order_cancel"
        try:
          await self.bot.wait_for("reaction_add", check = check)
        except:
          await ctx.send("刪除資料取消", delete_after = 5)
        else:
          data["subscribers"][data['artists'][artist][0]].remove(artist)
          del data["artists"][artist]
          await SUBSCRIBE.print_overview(self, data)
          try:
            writeFile("subscribe&update", data)
          except Exception as e:
            await ctx.send(f"刪除錯誤， {e}", delete_after = 5)
            print(e)
          else:
            await ctx.send("刪除資料完畢", delete_after = 5)
        finally:
          await msg.delete()
      else:
        await ctx.send(f"無人訂閱 {artist}", delete_after = 5)
    
  @commands.command()
  async def update(self, ctx, artist):
    await ctx.message.delete()
    data = readFile("subscribe&update")
    if ctx.author.id in manager or ctx.author.mention == data["artists"][artist][0]:
      data["artists"][artist][1] = (ctx.message.created_at + datetime.timedelta(hours= 8)).strftime("%m.%d")
      try:
        writeFile("subscribe&update", data)
      except Exception as e:
        await ctx.send(f"更新錯誤， {e}", delete_after = 5)
        print(e)
      else:
        await ctx.send("更新完畢", delete_after = 5)
        await ctx.send(f"{data['artists'][artist][0]} 更新了 `{artist}`\n預覽：{data['subscribers'][ctx.author.mention][0]}\n下載：{data['subscribers'][ctx.author.mention][1]}")
    else:
      await ctx.send(f"你不是 `{artist}` 的訂閱者", delete_after = 5)

  """@commands.command()
  async def stopUpdate(self, ctx, name):    #停更
    pass"""

  @commands.command()
  async def check(self, ctx):
    pass
  
  @commands.command(aliases = ["resub"])
  async def change_subscriber(self, ctx, artist, newSubscriber):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and mention_vaild(newSubscriber):
      try:
        newSubscriber = newSubscriber.replace("!", "")
      except:
        print(newSubscriber)
      data = readFile("subscribe&update")
      if newSubscriber in data["subscribers"].keys():
        msg = await ctx.send(f"請確認 `{artist}` 由 {data['artists'][artist][0]} 改為 {newSubscriber} 訂閱")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{CROSS MARK}")
        def check(reaction, user):
            if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}" and reaction.message.id == msg.id and user == ctx.author:
              return True
            elif str(reaction.emoji) == "\N{CROSS MARK}" and reaction.message.id == msg.id and user == ctx.author:
              raise "order_cancel"
        try:
          await self.bot.wait_for("reaction_add", check = check)
        except:
          await ctx.send("更改訂閱者取消", delete_after = 5)
        else:
          data["subscribers"][data["artists"][artist][0]].remove(artist)
          data["subscribers"][newSubscriber].append(artist)
          data["artists"][artist][0] = newSubscriber
          await SUBSCRIBE.print_overview(self, data)
          try:
            writeFile("subscribe&update", data)
          except Exception as e:
            await ctx.send(f"更改失敗， {e}", delete_after = 5)
            print(e)
          else:
            await ctx.send("更改完成", delete_after = 5)
        finally:
          await msg.delete()
      else:
        await ctx.send("新訂閱者不在訂閱者名單內", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)
  
  @commands.command(aliases = [])
  async def overview(self, ctx):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and ctx.channel.id == 675956755112394753:
      data = readFile("subscribe&update")
      setting = readFile("setting")
      message = await self.bot.get_channel(675956755112394753).fetch_message(setting["overview"])
      await message.delete()
      await SUBSCRIBE.print_overview(self, data)
    else:
      await ctx.send("沒有權限或頻道錯誤", delete_after = 5)
  
  @commands.command()
  async def info(self, ctx):
    pass
  
  @commands.command()
  async def edit_artist(self, ctx, originalName, newName):
    pass

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    setting = readFile("setting")
    if message.id == setting["overview"]:
      setting["overview"] = 0
      writeFile("setting", setting)

'''  @commands.command()
  async def upload(self, ctx):
    try:
      r = Redis(connection_pool=pool, decode_responses=True)
      data = readFile("subscribe&update")
      for key, value in data.items():
        r.set(key, str(value))
    except Exception as e:
      await ctx.send("上傳失敗", delete_after = 5)
      print(e)
    else:
      await ctx.send("上傳結束",delete_after = 5)
    finally:
      pool.disconnect()'''

def setup(bot):
  bot.add_cog(SUBSCRIBE(bot))