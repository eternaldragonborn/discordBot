import datetime
from core.classes import Cog_Ext
import discord
from discord.ext import commands
from core.wrFiles import readFile, writeFile, get_data, set_data
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice

guildID = [669934356172636199, 719132687897591808]

tz = datetime.timezone(datetime.timedelta(hours=8))
def get_time(): 
  return datetime.datetime.now(tz)

async def auth(ctx):
  if (ctx.channel.category_id in [719132688392519720, 696655511197712414] and ctx.channel.id != 675956755112394753) \
    and ctx.author.id in [590430031281651722, 384233645621248011, 546614210243854337]:
    return True
  else:
    await ctx.send("沒有權限或頻道錯誤，有疑問請詢問管理員", hidden=True)
    return False

def author_auth(ctx, target):
  return (ctx.channel.category_id in [719132688392519720, 696655511197712414] and ctx.channel.id != 675956755112394753) \
    and ctx.author.id == target

async def print_overview(self, data):
  setting = readFile("setting")
  message = "訂閱總覽(如需更改請告知管理者)\n>>> "
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
    await ctx.send("日期格式（MM-DD）錯誤(括弧不須輸入)", hidden=True)
    return False
  else:
    if not date <= (get_time().date()):
      await ctx.send("日期不合理(輸入的時間為未來式)", hidden=True)
      return False
    else:
      return True

async def change_data(self, ctx, data, message=None):
  try:
    set_data(data)
  except Exception as e:
    await ctx.send(f"更改失敗, {e}", delete_after = 5)
    await self.bot.get_channel(740196718477312061).send(f"{ctx.author.mention} 更改資料失敗， {e}")
    return False
  else:
    await print_overview(self, data)
    if message:
      await self.bot.get_channel(740196718477312061).send(f"{get_time().date()}\t{message}")
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
  def update_data(self, data):  
    data["subscribers"].update({self.name : [self.__url[0], self.__url[1], self.artists]})
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
    if self.__url[0]:  return f"預覽：\n{self.__url[0]}\n下載：\n{self.__url[1]}"
    else:  return f"預覽：無\n下載：\n{self.__url[1]}"
  def DLurl(self):
    return self.__url[1]
    
class Artist():
  def __init__(self, artist, data):
    self.name = artist
    self.subscriber = data[artist][0]
    self.lastUpdate = data[artist][1]
    self.mark = data[artist][2]
    self.statu = data[artist][3]    #0:普通，1:訂閱後未更新，2:本月無更新
  def update_data(self, data):  
    data["artists"].update({self.name : [self.subscriber, self.lastUpdate, self.mark, self.statu]})
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

  @cog_ext.cog_subcommand(base='manage', subcommand_group='subscriber', name='add', 
                    description='新增訂閱者，限管理員使用', guild_ids=guildID,
                    options=[
                      create_option(name='subscriber', description='新訂閱者', option_type=6, required=True),
                      create_option(name='download_url', description='下載網址', option_type=3, required=True),
                      create_option(name='preview_url', description='預覽網址', option_type=3, required=False)
                    ])
  async def new_subscriber(self, ctx, subscriber, download_url, preview_url=None):
    if await auth(ctx):
      data = get_data()
      subscriber = subscriber.mention.replace('!', '')
      if subscriber in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 已在訂閱者名單", hidden=True)
      else:
        if preview_url != None:
          preview_url = preview_url.replace(' ', '\n')
        download_url = download_url.replace(' ', '\n')
        subscriberData = Subscriber(subscriber, {subscriber : [preview_url, download_url, []]})
        subscriberData.update_data(data)
        message = f"新訂閱者:{subscriber}(by {ctx.author.mention})"
        await ctx.send(message)
        await change_data(self, ctx, data, message)

  @cog_ext.cog_subcommand(base='manage', subcommand_group='subscriber', name='delete', 
                    description='刪除訂閱者及其訂閱的繪師資料，限管理員使用', guild_ids=guildID,
                    options=[
                      create_option(name='subscriber', description='欲刪除的訂閱者', option_type=6, required=True)
                    ])
  async def delete_subscriber(self, ctx, subscriber):
    if await auth(ctx):
      data = get_data()
      subscriber = subscriber.mention.replace('!', '')
      if subscriber in data["subscribers"].keys():
        target = Subscriber(subscriber, data["subscribers"])
        message = f"請確認刪除 {target.name} 的資料"
        if len(target.artists) != 0:
          message += "，包含繪師："
          for artist in target.artists:
            message += f"`{artist}`"
            if artist != target.artists[-1]:
              message += "、"
        msg = await ctx.send(message)
        if await action_check(self, msg, ctx.author):
          for artist in target.artists:
            del data["artists"][artist]
          del data["subscribers"][subscriber]
          message = f"訂閱紀錄：{ctx.author.mention} 刪除了 {subscriber} 的資料"
          await ctx.send(message)
          await change_data(self, ctx, data, message)
        else:
          await ctx.send("刪除訂閱者資料取消", hidden=True)
        await msg.delete()
      else:
        await ctx.send(f"{subscriber} 不在訂閱者名單內", hidden=True)

  @cog_ext.cog_subcommand(base='manage', subcommand_group='artist', name='add',
                    description='新增訂閱紀錄，限管理員使用', guild_ids=guildID,
                    options=[
                      create_option(name='subscriber', description='訂閱者', option_type=6, required=True),
                      create_option(name='artist', description='繪師', option_type=3, required=True),
                      create_option(name='mark', description='備註，將顯示於繪師名後方', option_type=3, required=False)
                    ])
  async def subscribe(self, ctx, subscriber, artist, mark=""):
    if await auth(ctx):
      lastUpdate=(get_time()-datetime.timedelta(days = 31)).strftime("%Y-%m-%d")
      subscriber = subscriber.mention.replace('!', '')
      data = get_data()
      if artist in data["artists"].keys():
        await ctx.send(f"繪師 `{artist}` 已有訂閱紀錄", delete_after = 5)
      elif subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      else:
        if mark:
          mark = f"({mark})"
        new_subscribe = Artist(artist, {artist : [subscriber, lastUpdate, mark, 1]})
        msg = await ctx.send(f"請確認 {subscriber} 訂閱 `{artist}`{mark}")
        if not await action_check(self, msg, ctx.author):
          await ctx.send("新增資料取消", delete_after = 5)
        else:
          new_subscribe.update_data(data)
          target = Subscriber(subscriber, data["subscribers"])
          target.add_artist(artist, data)
          message = f"訂閱紀錄：{subscriber} 訂閱了 `{artist}`(by{ctx.author.mention})"
          await ctx.send(message)
          await change_data(self, ctx, data, message)
      await msg.delete()

  @cog_ext.cog_subcommand(base='manage', subcommand_group='artist', name='delete',
                    description='取消訂閱，限管理員使用', guild_ids=guildID,
                    options=[
                      create_option(name='artist', description='繪師名', option_type=3, required=True)
                    ])
  async def unsubscribe(self, ctx, artist):
    if await auth(ctx):
      data = get_data()
      if artist in data["artists"].keys():
        msg = await ctx.send(f"請確認 {data['artists'][artist][0]} 取消訂閱 `{artist}`")
        if not await action_check(self, msg, ctx.author):
          await ctx.send("刪除資料取消", delete_after = 5)
        else:
          subscriber = Subscriber(data['artists'][artist][0], data["subscribers"])
          subscriber.del_artist(artist, data)
          del data["artists"][artist]
          message = f"訂閱紀錄：{subscriber.name} 取消訂閱 `{artist}`(by {ctx.author.mention})"
          await ctx.send(message)
          await change_data(self, ctx, data, message)
        await msg.delete()
      else:
        await ctx.send(f"無人訂閱 {artist}", delete_after = 5)

  @cog_ext.cog_subcommand(base='manage', subcommand_group='artist', name='change_subscriber', 
                    description='更改訂閱者，限管理員使用', guild_ids=guildID,
                    options=[
                      create_option(name='artist', description='繪師名', option_type=3, required=True),
                      create_option(name='newsubscriber', description='新訂閱者', option_type=6, required=True)
                    ])
  async def change_subscriber(self, ctx, artist, newsubscriber):
    if await auth(ctx):
      newsubscriber = newsubscriber.mention.replace('!', '')
      data = get_data()
      if newsubscriber in data["subscribers"].keys() and artist in data['artists'].keys():
        oldSubscriber = Subscriber(data['artists'][artist][0], data["subscribers"])
        newSubscriber = Subscriber(newsubscriber, data["subscribers"])
        artist = Artist(artist, data["artists"])
        msg = await ctx.send(f"請確認 `{artist.name}` 由 {oldSubscriber.name} 改為 {newSubscriber.name} 訂閱")
        if not await action_check(self, msg, ctx.author):
          await ctx.send("更改訂閱者取消", delete_after = 5)
        else:
          artist.change_subscriber(oldSubscriber, newSubscriber, data)
          message = f"訂閱紀錄：{ctx.author.mention} 將 `{artist.name}` 由 {oldSubscriber.name} 改為 {newSubscriber.name} 訂閱"
          await ctx.send(message)
          await change_data(self, ctx, data, message)
        await msg.delete()
      else:
        await ctx.send("新訂閱者不在訂閱者名單內或繪師尚未被訂閱", delete_after = 5)
    else:
      await ctx.send("沒有權限或無此ID", delete_after = 5)
  
  @cog_ext.cog_subcommand(base='subscribe', description='更新常態訂閱的繪師圖包', guild_ids=guildID,
                    options=[
                      create_option(name='artists', description='要更新的繪師名，可一次更新多個繪師，於繪師名之間加上","即可', option_type=3, required=True),
                      create_option(name='timestamp', description='更新日期(mm-dd)，當日更新則不必輸入', option_type=3, required=False)
                    ])
  async def update(self, ctx, artists, timestamp = None):
    data = get_data()
    artists = artists.split(",")
    if timestamp == None:
      timestamp = str(get_time().date())
    else:
      timestamp = f"{get_time().year}-{timestamp}"
    if await date_valid(ctx, timestamp):
      for artist in artists:
        if artist in data["artists"].keys():
          subscriber = Subscriber(data['artists'][artist][0], data["subscribers"])
          if author_auth(ctx, int(subscriber.name[2:-1])) or await auth(ctx):
            artist = Artist(artist, data["artists"])
            artist.update(timestamp, 0, data)
            if await change_data(self, ctx, data, f"{subscriber.name} 於 {timestamp} 更新了 `{artist.name}`"):
              await ctx.send(f"{subscriber.name} 於 `{timestamp}` 更新了 `{artist.name}`\n>>> {subscriber.print_url()}")
          else:
            await ctx.send(f"你不是 `{artist}` 的訂閱者或頻道錯誤", delete_after = 5)
            break
        else:
          await ctx.send(f"無`{artist}`的訂閱紀錄", delete_after = 5)

  @cog_ext.cog_subcommand(base='subscribe', description='繪師本月無更新圖包', guild_ids=guildID,
                    options=[
                      create_option(name='artists', description='無更新的繪師名，可一次更新多個繪師，於各繪師名間加上","即可',option_type=3, required=True)
                    ])
  async def noupdate(self, ctx, artists):
    data = get_data()
    artists = artists.split(",")
    for artist in artists:
      if artist in data["artists"].keys():
        artist = Artist(artist, data["artists"])
        if author_auth(ctx, int(artist.subscriber[2:-1])) or auth(ctx):
          artist.update(get_time().strftime("%Y-%m-%d"), 2, data)
          if await change_data(self, ctx, data, f"{artist.subscriber}：`{artist.name}`本月沒有更新"):
            await ctx.send(f"> `{artist.name}` 本月沒有更新")
        else:
          await ctx.send(f"你不是 `{artist.name}` 的訂閱者", delete_after = 5)
      else:
        await ctx.send("無此繪師的訂閱紀錄", delete_after = 5)
  
  @cog_ext.cog_subcommand(base='subscribe', name='editURL', description='更改網址', guild_ids=guildID,
                    options=[
                      create_option(name='item', description='要更改的網址項目', option_type=4, required=True, 
                      choices=[
                        create_choice(0, '預覽網址'),
                        create_choice(1, '下載網址')
                      ]),
                      create_option(name='url', description='新網址，空格將自動取代為換行', option_type=3, required=True),
                      create_option(name='subscriber', description='更改網址的訂閱者，限管理員使用', option_type=6, required=False)
                    ])
  async def edit_subscriber(self, ctx, item, url, subscriber=None):
    if subscriber == None:
      subscriber = ctx.author.mention.replace('!', '')
    else:
      subscriber = subscriber.mention.replace('!', '')
    if url == 'None':
      url = None
    else:
      url = url.split(' ')
      url = '\n'.join(url)
    if author_auth(ctx, subscriber) or await auth(ctx):
      data = get_data()
      if subscriber not in data["subscribers"].keys():
        await ctx.send(f"{subscriber} 不在訂閱者名單內", delete_after = 5)
      else:
        subscriber = Subscriber(subscriber, data["subscribers"])
        subscriber.edit_url(item, url, data)
        await change_data(self, ctx, data)
        await ctx.send("更改完畢", hidden=True)
    else:
      await ctx.send("沒有權限", delete_after = 5)


  async def info(self, ctx, target, target_type):
    if ctx.channel.id == 681543745824620570 or ctx.channel.id == 719132688392519725:
      data = get_data()
      if target_type == 0:
        if target in data['subscribers']:
          subscriber = Subscriber(target, data["subscribers"])
          message = f"{subscriber.name}：\n>>> "
          message += "訂閱繪師："
          if len(subscriber.artists) == 0:
            message += "無\n"
          else:
            for artist in subscriber.artists:
              artist = Artist(artist, data["artists"])
              message += f" `{artist.name}`{artist.mark} "
              if artist.name == subscriber.artists[-1]:
                message += "\n"
              else:
                message += "、"
          message += subscriber.print_url()
          await ctx.send(message, hidden=True)
        else:
          await ctx.send("無此訂閱者")
      elif target_type == 1:
        if target in data['artists']:
          artist = Artist(target, data["artists"])
          subscriber = Subscriber(artist.subscriber, data["subscribers"])
          message = f"`{artist.name}`{artist.mark}：\n>>> 訂閱者： {subscriber.name}\n更新狀態："
          if datetime.date.fromisoformat(artist.lastUpdate).month == get_time().month:
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
          await ctx.send(message, hidden=True)
        else:
          await ctx.send("無人訂閱此繪師", delete_after = 5)
    else:
      await ctx.send("頻道錯誤", delete_after = 5)

  @cog_ext.cog_subcommand(base='subscribe', subcommand_group='info', name='artist', description='查詢繪師資料', guild_ids=guildID)
  async def info_artist(self, ctx, artist):
    await self.info(self, ctx, artist, 1)

  @cog_ext.cog_subcommand(base='subscribe', subcommand_group='info', name='subscriber', description='查詢訂閱者資料', guild_ids=guildID)
  async def info_subscriber(self, ctx, subscriber:discord.Member):
    subscriber = subscriber.mention.replace('!', '')
    await self.info(self, ctx, subscriber, 0)

  @cog_ext.cog_subcommand(base='manage', description='檢查超過30天未更新的訂閱者，管理員用', guild_ids=guildID)
  async def check(self, ctx):
    if await auth(ctx) and ctx.channel.id == 681543745824620570:
      message = "超過30天（含）未更新：\n>>> "
      data = get_data()
      for subscriber in data["subscribers"].keys():
        subscriber = Subscriber(subscriber, data["subscribers"])
        notupdate = []
        for artist in subscriber.artists:
          artist = Artist(artist, data["artists"])
          lastupdate = datetime.date.fromisoformat(artist.lastUpdate)
          since_lastupdate = get_time().date() - lastupdate
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

  @cog_ext.cog_subcommand(base='subscribe', description='上傳非常態訂閱的圖包', guild_ids=guildID,
                    options=[
                      create_option(name='author', description='圖包作者', option_type=3, required=False),
                      create_option(name='subscriber', description='上傳的訂閱者，限管理員使用', option_type=6, required=False)
                    ])
  async def upload(self, ctx, author = "", subscriber = ""):
    if subscriber != "":
      subscriber = subscriber.mention.replace("!", "")
    else:
      subscriber = ctx.author.mention.replace('!', '')
    if await auth(ctx) or author_auth(ctx, subscriber):
      data = get_data()
      if subscriber in data["subscribers"].keys():
        subscriber = Subscriber(subscriber, data["subscribers"])
        if not author:
          await ctx.send(f"{subscriber.name} 上傳了圖包\n>>> 下載網址：\n{subscriber.DLurl()}")
        else:
          await ctx.send(f"{subscriber.name} 上傳了 `{author}` 的圖包\n>>> 下載網址：\n{subscriber.DLurl()}")
      else:
        await ctx.send("無網址資料", delete_after = 3)
    
  @commands.Cog.listener()
  async def on_message_delete(self, message):
    setting = readFile("setting")
    if message.id == setting["overview"]:
      setting["overview"] = 0
      writeFile("setting", setting)
    elif message.id == setting["info"]:
      setting["info"] = 0
      writeFile("setting", setting)

  @commands.command(hidden = True)
  async def uploadData(self, ctx):
    if await self.bot.is_owner(ctx.author):
      data = readFile("subscribeData")
      try:
        set_data(data)
      except Exception as e:
        print(e)
      else:
        await print_overview(self, data)
        await ctx.send("上傳完成", delete_after = 5)

  @commands.command(hidden = True)
  async def pull(self, ctx):
    await ctx.message.delete()
    if await self.bot.is_owner(ctx.author):
      data = get_data()
      writeFile("subscribeData", data)

  @commands.command(hidden = True)
  async def overview(self, ctx):
    await ctx.message.delete()
    if await self.bot.is_owner(ctx.author):
      setting = readFile("setting")
      if setting["overview"] != 0:
        msg = await ctx.fetch_message(setting["overview"])
        await msg.delete()
        setting["overview"] = 0
      data = get_data()
      await print_overview(self, data)
      

def setup(bot):
  bot.add_cog(SUBSCRIBE(bot))