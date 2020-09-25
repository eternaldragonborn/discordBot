import datetime
from core.classes import Cog_Ext
import discord
from discord.ext import commands
from core.wrFiles import readFile, writeFile, get_data, set_data
import re

tz = datetime.timezone(datetime.timedelta(hours=8))

def auth(ctx):
  return (ctx.channel.category_id in [719132688392519720, 696655511197712414] and ctx.channel.id != 675956755112394753) \
    and ctx.author.id in [590430031281651722, 384233645621248011, 546614210243854337]

def author_auth(ctx, target):
  return (ctx.channel.category_id in [719132688392519720, 696655511197712414] and ctx.channel.id != 675956755112394753) \
    and ctx.author.id == target

async def print_overview(self, data):
  setting = readFile("setting")
  message = "訂閱總覽(如需更改請告知管理者，繪師名中的空格皆以_取代)\n>>> "
  for subscriber in data["subscribers"].keys():
    subscriber = Subscriber(subscriber, data["subscribers"])
    message+=f"{subscriber.name}："
    if len(subscriber.artists) == 0:
      message += "\n"
    else:
      for artist in subscriber.artists:
        artist = Artist(artist, data["artists"])
        if artist.name != subscriber.artists[-1]:
          message+=f"`{artist.name}`{artist.mark}、"
        else:
          message+=f"`{artist.name}`{artist.mark}\n"
  try:
    overview = await self.bot.get_channel(675956755112394753).fetch_message(setting["overview"])
  except:
    msg = await self.bot.get_channel(675956755112394753).send(message)
    await msg.pin()
    setting["overview"] = msg.id
    writeFile("setting", setting)
  else:
    await overview.edit(content = message)

async def date_valid(ctx, date):
  try:
    date = datetime.date.fromisoformat(date)
  except:
    await ctx.send("日期格式（MM-DD）錯誤", delete_after = 5)
    return False
  else:
    if not date <= (datetime.datetime.now(tz).date()):
      await ctx.send("日期不合理", delete_after = 5)
      return False
    else:
      return True

async def change_data(self, ctx, data, message=None):
  time = datetime.datetime.now(tz)
  try:
    set_data(data)
  except Exception as e:
    await ctx.send(f"更改失敗, {e}", delete_after = 5)
    await self.bot.get_channel(740196718477312061).send(f"{ctx.author.mention} 更改資料失敗， {e}")
    return False
  else:
    await ctx.send("更改完成", delete_after = 5)
    await print_overview(self, data)
    if message:
      await self.bot.get_channel(740196718477312061).send(f"{time.date()}\t{message}")
    return True

async def action_check(self, msg, author):
  await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
  await msg.add_reaction("\N{CROSS MARK}")
  def check(reaction, user):
    if reaction.message.id == msg.id and user == author:
      if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}":
        return True
      elif str(reaction.emoji) == "\N{CROSS MARK}":
        raise "order_cancel"
  try:  await self.bot.wait_for("reaction_add", check = check)
  except:  return False
  else:  return True

class Subscriber():
  def __init__(self, subscriber, data):
    self.name = subscriber
    self.__url = data[subscriber][0:2]
    self.artists = data[subscriber][2]
  def update_data(self, data):  data["subscribers"].update({self.name : [self.__url[0], self.__url[1], self.artists]})
  def edit_url(self, target, url, data):  
    self.__url[target] = url
    self.update_data(data)
  def add_artist(self, artist, data):  
    self.artists.append(artist)
    self.update_data(data)
  def del_artist(self, artist, data):  
    self.artists.remove(artist)
    self.update_data(data)
  def print_url(self):
    if self.__url != None:  return f"預覽：\n{self.__url[0]}\n下載：\n{self.__url[1]}"
    else:  return f"預覽：無\n下載：\n{self.__url[1]}"
    
class Artist():
  def __init__(self, artist, data):
    self.name = artist
    self.subscriber = data[artist][0]
    self.lastUpdate = data[artist][1]
    self.mark = data[artist][2]
    self.statu = data[artist][3]    #0:普通，1:訂閱後未更新，2:本月無更新
  def update_data(self, data):  data["artists"].update({self.name : [self.subscriber, self.lastUpdate, self.mark, self.statu]})
  def change_subscriber(self, oldSubscriber, newSubscriber, data):  
    self.subscriber = newSubscriber.name
    self.update_data(data)
    oldSubscriber.del_artist(self.name, data)
    newSubscriber.add_artist(self.name, data)
  def update(self, date, statu, data):
    self.lastUpdate = date
    self.statu = statu
    self.update_data(data)

class SUBSCRIBE(Cog_Ext):

  @commands.command(aliases = ["add_suber"])
  async def new_subscriber(self, ctx, subscriber, download_url, preview_url=None):
    await ctx.message.delete()
    if auth(ctx):
      data = get_data()
      subscriber = subscriber.replace("!", "")
      if subscriber in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 已在訂閱者名單", delete_after = 5)
      else:
        subscriberData = Subscriber(subscriber, {subscriber : [preview_url, download_url, []]})
        subscriberData.update_data(data)
        await change_data(self, ctx, data, f"新訂閱者；{subscriber}(by {ctx.author.mention})")
    else:
      await ctx.send("沒有權限", delete_after = 5)

  @commands.command(aliases = ["del_suber"])
  async def delete_subscriber(self, ctx, subscriber):
    await ctx.message.delete()
    if auth(ctx):
      data = get_data()
      if subscriber in data["subscribers"].keys():
        target = Subscriber(subscriber, data["subscribers"])
        message = f"請確認刪除 {target.name} 的資料"
        if len(target.artists) != 0:
          message += "，包含繪師："
          for artist in target.artists:
            message += f"`{artist}`"
            if artist != target.artists[-1]:
              message += f"、"
        msg = await ctx.send(message)
        if await action_check(self, msg, ctx.author):
          for artist in target.artists:
            del data["artists"][artist]
          del data["subscribers"][subscriber]
          await change_data(self, ctx, data, f"{ctx.author.mention} 刪除了 {subscriber} 的資料")
        else:
          await ctx.send("刪除訂閱者資料取消", delete_after = 5)
        await msg.delete()
      else:
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
    else:
      await ctx.send("沒有權限", delete_after = 5)

  @commands.command(aliases = ["sub"])
  async def subscribe(self, ctx, subscriber, artist, lastUpdate=(datetime.datetime.now(tz)-datetime.timedelta(days = 31)).strftime("%m-%d"), mark=""):
    await ctx.message.delete()
    if auth(ctx):
      subscriber = subscriber.replace("!", "")
      data = get_data()
      #artist = artist.title()
      if artist in data["artists"].keys():
        await ctx.send(f"繪師 `{artist}` 已有訂閱紀錄", delete_after = 5)
      elif subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      else:
        lastUpdate = f"{datetime.datetime.now(tz).year}-{lastUpdate}"
        if mark:
          mark = f"({mark})"
        if await date_valid(ctx, lastUpdate):
          if lastUpdate == (datetime.datetime.now(tz)-datetime.timedelta(days = 31)).strftime("%Y-%m-%d"):
            status = 1
          else:
            status = 0
          new_subscribe = Artist(artist, {artist : [subscriber, lastUpdate, mark, status]})
          msg = await ctx.send(f"請確認 {subscriber} 訂閱 `{artist}`{mark}，最後更新於 {lastUpdate}")
          if not await action_check(self, msg, ctx.author):
            await ctx.send("新增資料取消", delete_after = 5)
          else:
            new_subscribe.update_data(data)
            target = Subscriber(subscriber, data["subscribers"])
            target.add_artist(artist, data)
            await change_data(self, ctx, data, f"{subscriber} 訂閱了 `{artist}`(by {ctx.author.mention})")
      await msg.delete()
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)

  @commands.command(aliases = ["unsub"])
  async def unsubscribe(self, ctx, artist):
    await ctx.message.delete()
    if auth(ctx):
      data = get_data()
      #artist = artist.title()
      if artist in data["artists"].keys():
        msg = await ctx.send(f"請確認 {data['artists'][artist][0]} 取消訂閱 `{artist}`")
        if not await action_check(self, msg, ctx.author):
          await ctx.send("刪除資料取消", delete_after = 5)
        else:
          subscriber = Subscriber(data['artists'][artist][0], data["subscribers"])
          subscriber.del_artist(artist, data)
          del data["artists"][artist]
          await change_data(self, ctx, data, f"{subscriber.name} 取消訂閱 `{artist}`(by {ctx.author.mention})")
        await msg.delete()
      else:
        await ctx.send(f"無人訂閱 {artist}", delete_after = 5)

  @commands.command(aliases = ["resub"])
  async def change_subscriber(self, ctx, artist, subscriber):
    await ctx.message.delete()
    if auth(ctx):
      subscriber = subscriber.replace("!", "")
      data = get_data()
      #artist = artist.title()
      if subscriber in data["subscribers"].keys() and artist in data['artists'].keys():
        oldSubscriber = Subscriber(data['artists'][artist][0], data["subscribers"])
        newSubscriber = Subscriber(subscriber, data["subscribers"])
        artist = Artist(artist, data["artists"])
        msg = await ctx.send(f"請確認 `{artist.name}` 由 {oldSubscriber.name} 改為 {newSubscriber.name} 訂閱")
        if not await action_check(self, msg, ctx.author):
          await ctx.send("更改訂閱者取消", delete_after = 5)
        else:
          artist.change_subscriber(oldSubscriber, newSubscriber, data)
          await change_data(self, ctx, data, f"{ctx.author.mention} 將 `{artist.name}` 由 {subscriber} 改為 {newSubscriber.name} 訂閱")
        await msg.delete()
      else:
        await ctx.send("新訂閱者不在訂閱者名單內或繪師尚未被訂閱", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)
  
  @commands.command()
  async def update(self, ctx, artist, date = datetime.datetime.now(tz).date().strftime("%m-%d")):
    await ctx.message.delete()
    data = get_data()
    #artist = artist.title()
    if artist in data["artists"].keys():
      subscriber = Subscriber(data['artists'][artist][0], data["subscribers"])
      if author_auth(ctx, int(subscriber.name[2:-1])) or auth(ctx):
        date = f"{datetime.datetime.now(tz).year}-{date}"
        if await date_valid(ctx, date):
          artist = Artist(artist, data["artists"])
          artist.update(date, 0, data)
          if await change_data(self, ctx, data, f"{subscriber.name} 於 {date} 更新了 `{artist.name}`"):
            await ctx.send(f"{subscriber.name} 於 `{date}` 更新了 `{artist.name}`\n>>> {subscriber.print_url()}")
      else:
        await ctx.send(f"你不是 `{artist}` 的訂閱者或頻道錯誤", delete_after = 5)
    else:
      await ctx.send("無此繪師的訂閱紀錄", delete_after = 5)

  @commands.command()
  async def noupdate(self, ctx, artist):
    await ctx.message.delete()
    data = get_data()
    if artist in data["artists"].keys():
      artist = Artist(artist, data["artists"])
      if author_auth(ctx, artist.subscriber[2:-1]) or auth(ctx):
        artist.update((ctx.message.created_at + datetime.timedelta(hours= 8)).strftime("%Y-%m-%d"), 2, data)
        if await change_data(self, ctx, data, f"{artist.subscriber}：`{artist.name}`本月沒有更新"):
          await ctx.send(f"> `{artist.name}` 本月沒有更新")
      else:
        await ctx.send(f"你不是 `{artist.name}` 的訂閱者", delete_after = 5)
    else:
      await ctx.send("無此繪師的訂閱紀錄", delete_after = 5)
  
  @commands.command(aliases = ["e_url"])
  async def edit_subscriber(self, ctx, item:int , *, s):
    await ctx.message.delete()
    s = s.split(" ")
    if re.match(r"<@!?\d{18}>", s[-1]):
      subscriber = s[-1]
      url = s[:-1]
    else:
      subscriber = ctx.author.mention
      url = s
    url = str(url)[1:-1].replace("'", "")
    url = url.replace(", ", "\n")
    subscriber = subscriber.replace("!", "")
    if author_auth(ctx, int(subscriber[2:-1])) or auth(ctx):
      data = get_data()
      if subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      elif not 0 <= item <= 1:
        await ctx.send("更改項目編號(0:預覽網址，1:下載網址)錯誤",delete_after = 5)
      else:
        print(url)
        subscriber = Subscriber(subscriber, data["subscribers"])
        subscriber.edit_url(item, url, data)
        await change_data(self, ctx, data)
    else:
      await ctx.send("沒有權限", delete_after = 5)

  @commands.command()
  async def info(self, ctx, target):
    await ctx.message.delete()
    if ctx.channel.id == 681543745824620570 or ctx.channel.id == 719132688392519725:
      data = get_data()
      if re.match(r"<@!?\d{18}>", target):
        target = target.replace("!","")
      if target in data['subscribers']:
        subscriber = Subscriber(target, data["subscribers"])
        message = f"{subscriber.name}：\n>>> "
        message += "訂閱繪師："
        for artist in subscriber.artists:
          artist = Artist(artist, data["artists"])
          message += f" `{artist.name}`{artist.mark} "
          if artist.name == subscriber.artists[-1]:
            message += "\n"
          else:
            message += "、"
        message += subscriber.print_url()
        await ctx.send(message, delete_after = 15)
      elif target in data['artists']:
        artist = Artist(target, data["artists"])
        subscriber = Subscriber(artist.subscriber, data["subscribers"])
        message = f"`{artist.name}`{artist.mark}：\n>>> 訂閱者： {subscriber.name}\n更新狀態："
        if datetime.date.fromisoformat(artist.lastUpdate).month == datetime.datetime.now(tz).month:
          if artist.statu == 0:
            message += "本月已更新\n"
          elif artist.statu == 2:
            message += "繪師本月無更新\n"
        else:
          if artist.statu == 0:
            message += f"本月尚未更新，上次更新日期為 {artist.lastUpdate}\n"
          elif artist.statu == 1:
            message += "新增訂閱資料後未更新\n"
        message += subscriber.print_url()
        await ctx.send(message, delete_after = 15)
      else:
        await ctx.send(f"無 {target} 的資料", delete_after = 5)
    else:
      await ctx.send("頻道錯誤", delete_after = 5)

  @commands.command()
  async def check(self, ctx):
    if auth(ctx) and ctx.channel.id == 681543745824620570:
      message = "超過30天（含）未更新：\n>>> "
      data = get_data()
      for subscriber in data["subscribers"].keys():
        subscriber = Subscriber(subscriber, data["subscribers"])
        notupdate = []
        for artist in subscriber.artists:
          artist = Artist(artist, data["artists"])
          lastupdate = datetime.date.fromisoformat(artist.lastUpdate)
          since_lastupdate = datetime.datetime.now(tz).date() - lastupdate
          if since_lastupdate >= datetime.timedelta(days = 30):
            if artist.statu != 1:
              notupdate.append([artist.name, lastupdate.strftime("%m-%d")])
            elif artist.statu == 1:
              notupdate.append([artist.name, "新增訂閱資料後未更新"])
        if notupdate:
          message += f"{subscriber.name}："
          for info in notupdate:
            message += f"`{info[0]}`（{info[1]}）"
            if info != notupdate[-1]:
              message += "、"
            else:
              message += "\n"
      await ctx.send(message)
      await ctx.send("若已更新但還是在清單中，請確認更新時使用指令`+update 繪師 日期（mm-dd）`或告知管理者更新日期，繪師無更新請使用`+noupdate 繪師`")
    await ctx.message.delete()

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

def setup(bot):
  bot.add_cog(SUBSCRIBE(bot))