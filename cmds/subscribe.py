import datetime
from core.classes import Cog_Ext
import discord
from discord.ext import commands
from core.wrFiles import readFile, writeFile, get_data, set_data
import re

# {artists : {author : [subscriber, lastUpdate, mark, type(0:繪師, 1:訂閱後未更新, 2:本月無更新)]},
#  subscribers : {subscriber : [preview_url, download_url, artist...]}}
manager = [590430031281651722, 384233645621248011, 546614210243854337]

tz = datetime.timezone(datetime.timedelta(hours=8))

async def record(self, message):
  time = datetime.datetime.now(tz)
  await self.bot.get_channel(740196718477312061).send(f"{time.date()} {time.strftime('%H:%M')}\t{message}")
  '''with open("record.txt", "a") as f:
    f.write(f"{date}\t{message}\n")'''

def mention_valid(mention):
  if re.match('<@!?\d{18}>', mention):
    return True
  else:
    return False

def date_valid(date):
  try:
    date = datetime.date.fromisoformat(date)
  except Exception as e:
    print(e)
    raise "format_error"
  else:
    if not date <= (datetime.datetime.now(tz).date()):
      raise "日期不合理"
    else:
      return True

async def print_overview(self, data):
  setting = readFile("setting")
  message = "訂閱總覽(如需更改請告知管理者，繪師名中的空格皆以_取代)\n>>> "
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

class SUBSCRIBE(Cog_Ext):

  @commands.command(aliases = ["add_suber"])
  async def new_subscriber(self, ctx, subscriber, download_url, preview_url=None):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and mention_valid(subscriber) and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 670517724350382082):
      data = get_data()
      subscriber.replace("!", "")
      if subscriber in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 已在訂閱者名單", delete_after = 5)
      else:
        subscriberData = {subscriber : [preview_url, download_url]}
        data["subscribers"].update(subscriberData)
        try:
          set_data(data)
        except Exception as e:
          await ctx.send(f"新增錯誤， {e}", delete_after = 5)
          await record(self, f"{ctx.author.mention} 新增訂閱者失敗， {e}")
          print(e)
        else:
          await record(self, f"新訂閱者；{subscriber}(by {ctx.author.mention})")
          await print_overview(self, data)
          await ctx.send("訂閱者資料新增完畢", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此用戶", delete_after = 5)

  @commands.command(aliases = ["e_url"])
  async def edit_subscriber(self, ctx, item:int , url, subscriber =""):
    global manager
    await ctx.message.delete()
    if not subscriber:
      subscriber = ctx.author.mention.replace("!","")
    if (ctx.author.id in manager or ctx.author.id == int(subscriber[2:-1])) and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 719132688392519725):
      data = get_data()
      if subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      elif not 0 <= item <= 1:
        await ctx.send("更改項目編號錯誤(0:預覽網址，1:下載網址)",delete_after = 5)
      else:
        data["subscribers"][subscriber][item] = url
        try:
          set_data(data)
        except Exception as e:
          await ctx.send(f"修改資料錯誤, {e}", delete_after = 5)
          print(e)
        else:
          await ctx.send("網址更改完畢", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)
  
  @commands.command(aliases = ["sub"])
  async def subscribe(self, ctx, subscriber, artist, lastUpdate=(datetime.datetime.now(tz)-datetime.timedelta(days = 31)).strftime("%m-%d"), *, mark=""):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and mention_valid(subscriber) and (ctx.channel.id == 681543745824620570 or ctx.channel.id == 675956755112394753):
      subscriber = subscriber.replace("!", "")
      data = get_data()
      if artist in data["artists"].keys():
        await ctx.send(f"繪師 `{artist}` 已有訂閱紀錄", delete_after = 5)
      elif subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      else:
        lastUpdate = f"{datetime.datetime.now(tz).year}-{lastUpdate}"
        if mark:
          mark = f"({mark})"
        try:
          date_valid(lastUpdate)
        except:
          await ctx.send("日期格式(mm-dd)錯誤或不合理", delete_after = 5)
        else:
          if lastUpdate == (datetime.datetime.now(tz)-datetime.timedelta(days = 31)).strftime("%Y-%m-%d"):
            status = 1
          else:
            status = 0
          new_subscribe = {artist : [subscriber, lastUpdate, mark, status]}
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
            try:
              set_data(data)
            except Exception as e:
              await record(self, f"{ctx.author.mention}新增訂閱失敗，{e}")
              await ctx.send(f"新增錯誤， {e}", delete_after = 5)
              print(e)
            else:
              await record(self, f"{subscriber} 訂閱了 `{artist}`(by {ctx.author.mention})")
              await print_overview(self, data)
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
      data = get_data()
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
          subscriber = data['artists'][artist][0]
          data["subscribers"][subscriber].remove(artist)
          del data["artists"][artist]
          try:
            set_data(data)
          except Exception as e:
            await record(self, f"{ctx.author.mention}刪除訂閱資料失敗，{e}")
            await ctx.send(f"刪除錯誤， {e}", delete_after = 5)
            print(e)
          else:
            await record(self, f"{subscriber} 取消訂閱 `{artist}`(by {ctx.author.mention})")
            await print_overview(self, data)
            await ctx.send("刪除資料完畢", delete_after = 5)
        finally:
          await msg.delete()
      else:
        await ctx.send(f"無人訂閱 {artist}", delete_after = 5)
    
  @commands.command()
  async def update(self, ctx, artist, date =""):
    await ctx.message.delete()
    data = get_data()
    if artist in data["artists"].keys():
      if (ctx.author.id in manager or ctx.author.id == int(data["artists"][artist][0][2:-1])) or ctx.channel.id == 681543745824620570:
        if not date:
          date = datetime.datetime.now(tz).date()
          date = date.strftime("%Y-%m-%d")
        else:
          date = f"{datetime.datetime.now(tz).year}-{date}"
        subscriber = data['artists'][artist][0]
        try:
          date_valid(date)
        except:
          await ctx.send("日期格式(mm-dd)錯誤或不合理", delete_after = 5)
        else:
          data["artists"][artist][1] = date
          data["artists"][artist][3] = 0
          try:
            set_data(data)
          except Exception as e:
            await record(self, f"{subscriber} 更新失敗，{e}")
            await ctx.send(f"更新錯誤， {e}", delete_after = 5)
            print(e)
          else:
            await record(self, f"{subscriber} 於 {date} 更新了 `{artist}`")
            await ctx.send("更新完畢", delete_after = 5)
            await ctx.send(f"{subscriber} 於 `{date}` 更新了 `{artist}`\n>>> 預覽：{data['subscribers'][subscriber][0]}\n下載：{data['subscribers'][subscriber][1]}")
      else:
        await ctx.send(f"你不是 `{artist}` 的訂閱者或頻道錯誤", delete_after = 5)
    else:
      await ctx.send("無此繪師的訂閱紀錄", delete_after = 5)
  
  @commands.command(aliases = ["resub"])
  async def change_subscriber(self, ctx, artist, newSubscriber):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and mention_valid(newSubscriber):
      newSubscriber = newSubscriber.replace("!", "")
      data = get_data()
      if newSubscriber in data["subscribers"].keys() and artist in data['artists'].keys():
        subscriber = data['artists'][artist][0]
        msg = await ctx.send(f"請確認 `{artist}` 由 {subscriber} 改為 {newSubscriber} 訂閱")
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
          data["subscribers"][subscriber].remove(artist)
          data["subscribers"][newSubscriber].append(artist)
          data["artists"][artist][0] = newSubscriber
          try:
            set_data(data)
          except Exception as e:
            await ctx.send(f"更改失敗， {e}", delete_after = 5)
            print(e)
          else:
            await record(self, f"{ctx.author.mention} 將 `{artist}` 由 {subscriber} 改為 {newSubscriber} 訂閱")
            await print_overview(self, data)
            await ctx.send("更改完成", delete_after = 5)
        finally:
          await msg.delete()
      else:
        await ctx.send("新訂閱者不在訂閱者名單內或繪師尚未被訂閱", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)

  @commands.command(aliases = ["del_suber"])
  async def delete_subscriber(self, ctx, subscriber):
    global manager
    if ctx.author.id in manager:
      data = get_data()
      if subscriber in data["subscribers"].keys():
        pass
        message = f"請確認刪除 {subscriber} 的資料"
        if len(data["subscribers"][subscriber][2:]) == 0:
          msg = await ctx.send(message)
        else:
          message += "，包含繪師："
          for artist in data["subscribers"][subscriber][2:]:
            message += f"`{artist}`"
            if artist != data["subscribers"][subscriber][-1]:
              message += f"、"
        msg = await ctx.send(message)
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
          await ctx.send("刪除訂閱者資料取消", delete_after = 5)
        else:
          for artist in data["subscribers"][subscriber][2:]:
            del data["artists"][artist]
          del data["subscribers"][subscriber]
          try:
            set_data(data)
          except Exception as e:
            await ctx.send(f"刪除失敗， {e}", delete_after = 5)
            print(e)
          else:
            await record(self, f"{ctx.author.mention} 刪除了 {subscriber} 的資料")
            await print_overview(self, data)
            await ctx.send("刪除完畢", delete_after = 5)
          finally:
            await msg.delete()
      else:
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
    else:
      await ctx.send("沒有權限", delete_after = 5)
    await ctx.message.delete()
  
  @commands.command(aliases = [])
  async def overview(self, ctx):
    global manager
    await ctx.message.delete()
    if ctx.author.id in manager and ctx.channel.id == 675956755112394753:
      setting = readFile("setting")
      try:
        message = await self.bot.get_channel(675956755112394753).fetch_message(setting["overview"])
      except:
        pass
      else:
        await message.delete()
      data = get_data()
      await print_overview(self, data)
    else:
      await ctx.send("沒有權限或頻道錯誤", delete_after = 5)
  
  @commands.command()
  async def check(self, ctx):
    global manager
    if ctx.author.id in manager and ctx.channel.id == 681543745824620570:
      message = "超過30天（含）未更新：\n>>> "
      data = get_data()
      for subscriber, content in data["subscribers"].items():
        notupdate = []
        for artist in content[2:]:
          lastupdate = datetime.date.fromisoformat(data["artists"][artist][1])
          since_lastupdate = datetime.datetime.now(tz).date() - lastupdate
          if since_lastupdate >= datetime.timedelta(days = 30):
            if data['artists'][artist][3] != 1:
              notupdate.append([artist, lastupdate.strftime("%m-%d")])
            elif data['artists'][artist][3] == 1:
              notupdate.append([artist, "新增訂閱資料後未更新"])
        if notupdate:
          message += f"{subscriber}："
          for info in notupdate:
            message += f"`{info[0]}`（{info[1]}）"
            if info != notupdate[-1]:
              message += "、"
            else:
              message += "\n"
      await ctx.send(message)
      await ctx.send("若已更新但還是在清單中，請確認更新時使用指令`+update 繪師 日期（mm-dd）`或告知管理者更新日期，繪師無更新請使用`+noupdate 繪師`")
    await ctx.message.delete()

  @commands.command()
  async def noupdate(self, ctx, artist):
    await ctx.message.delete()
    data = get_data()
    if artist in data["artists"].keys():
      if ctx.author.id in manager or ctx.author.id == int(data["artists"][artist][0][2:-1]) and ctx.channel.id == 681543745824620570:
        data["artists"][artist][1] = (ctx.message.created_at + datetime.timedelta(hours= 8)).strftime("%Y-%m-%d")
        data["artists"][artist][3] = 2
        try:
          set_data(data)
        except Exception as e:
          await ctx.send(f"更新錯誤， {e}", delete_after = 5)
          print(e)
        else:
          await record(self, f"{ctx.author.mention}: `{artist}` 本月無更新")
          await ctx.send(f"> `{artist}` 本月沒有更新")
      else:
        await ctx.send(f"你不是 `{artist}` 的訂閱者", delete_after = 5)
    else:
      await ctx.send("無此繪師的訂閱紀錄", delete_after = 5)
  
  @commands.command()
  async def edit_artist(self, ctx, item, content):
    pass

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    setting = readFile("setting")
    if message.id == setting["overview"]:
      setting["overview"] = 0
      writeFile("setting", setting)
    elif message.id == setting["info"]:
      setting["info"] = 0
      writeFile("setting", setting)

  @commands.command()
  async def upload(self, ctx):
    await ctx.message.delete()
    if await self.bot.is_owner(ctx.author):
      data = readFile("subscribeData")
      try:
        set_data(data)
      except Exception as e:
        print(e)
      else:
        await print_overview(self, data)
        await ctx.send("上傳完成", delete_after = 5)

  @commands.command()
  async def pull(self, ctx):
    await ctx.message.delete()
    if await self.bot.is_owner(ctx.author):
      data = get_data()
      writeFile("subscribeData", data)

  @commands.command()
  async def info(self, ctx, target):
    await ctx.message.delete()
    if ctx.channel.id == 681543745824620570 or ctx.channel.id == 719132688392519725:
      data = get_data()
      if mention_valid(target):
        target = target.replace("!","")
      if target in data['subscribers']:
        message = f"{target}：\n>>> "
        message += "訂閱繪師："
        for artist in data['subscribers'][target][2:]:
          message += f" `{artist}`{data['artists'][artist][2]} "
          if artist == data['subscribers'][target][-1]:
            message += "\n"
          else:
            message += "、"
        message += f"預覽：{data['subscribers'][target][0]}\n下載：{data['subscribers'][target][1]}"
        await ctx.send(message, delete_after = 15)
      elif target in data['artists']:
        subscriber, lastupdate, mark, status = data['artists'][target]
        message = f"`{target}`{mark}：\n>>> 訂閱者： {subscriber}\n更新狀態："
        if datetime.date.fromisoformat(lastupdate).month == datetime.datetime.now(tz).month:
          if status == 0:
            message += "本月已更新"
          elif status == 2:
            message += "繪師本月無更新"
        else:
          if status == 0:
            message += f"本月尚未更新，上次更新日期為 {lastupdate}"
          elif status == 1:
            message += "新增訂閱資料後未更新"
        message += f"\n預覽：{data['subscribers'][subscriber][0]}\n下載：{data['subscribers'][subscriber][1]}"
        await ctx.send(message, delete_after = 15)
      else:
        await ctx.send(f"無 {target} 的資料", delete_after = 5)
    else:
      await ctx.send("頻道錯誤", delete_after = 5)

def setup(bot):
  bot.add_cog(SUBSCRIBE(bot))