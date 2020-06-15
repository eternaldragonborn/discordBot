import discord
from discord.ext import commands
from core.classes import Cog_Ext
from core.wrFiles import readFile
import random


is_started = False    #declear, lots of declear
in_game = False
initiator = ""  #莊家
participants = {}   #{name : [point, *cards]}
channel = ""  #遊玩的頻道
turn = 0
cards = []
players = []
point = readFile("cards")["point"]
player_num = 0
Round = 1
t_round = 0


def draw(player):  #抽牌
  global cards
  global point
  global participants
  random.shuffle(cards)
  card = cards.pop()    #考慮以random產生index
  participants[player][0] += point[card[1]]
  participants[player].append(card)
  return card

class BLACKJACK(Cog_Ext):

  async def end_game():
    global participants
    global channel
    global in_game
    global is_started
    global players
    global Round
    global turn
    maxpoint = 0 

    if len(participants.keys()) == 0:
      await channel.send("所有玩家皆爆牌，此局遊戲無贏家")
    else:
      winner = []
      msg = ""
      for player, point in participants.items():
        if point[0] > maxpoint:    
          maxpoint = point[0]
      for player, point in participants.items():
        if point[0] == maxpoint:    
          winner.append(player)
      if initiator in winner:
        msg += f"回合結束，莊家({initiator.mention})贏了，各玩家資訊：\n"
      else:
        msg += "回合結束，"
        for player in winner:
          if player != winner[-1]:
            msg += f" {player.mention} &"
          else:
            msg += f" {player.mention}"
        msg += " 贏了，各玩家資訊：\n"
      for player, point in participants.items():
        msg += f"{player.mention} : `{point[0]}` 點，手牌 :"
        for card in point[1:-1]:
          msg += f"`{card[0]}` `{card[1]}`、"
        msg += f"`{point[-1][0]}` `{point[-1][1]}`\n"
      msg += "** **"
      await channel.send(msg)

    if Round > t_round:
      await channel.send("遊戲結束")
      in_game = False
      is_started = False
      participants = {}
      players = []
      Round = 1
    else:
      turn = 0
      participants = {initiator : [0]}
      players.remove(initiator)
      for player in players:
        participants.setdefault(player, [0])
      await BLACKJACK.game()

  async def game():
    global in_game
    global is_started
    global players
    global initiator
    global cards
    global participants
    global turn
    global Round

    if not in_game and is_started:
      if len(list(participants.keys())) <= 1:
        await channel.send("遊戲人數不足", delete_after = 5)
        is_started = False
        participants = {}
      else:
        await channel.send("遊戲開始，由於bot一定時間內只能發5則訊息，若訊息卡住請稍帶數秒，`+p`可查詢點數")
        in_game = True
    if is_started and in_game:
      if turn == 0:  #回合開始
        cards = readFile("cards")["cards"]  #初始化牌組
        random.shuffle(players)
        players.append(initiator)
        await channel.send(f"第 {Round} 回合開始，要牌順序及明牌：")
        msg = ""
        for i, player in enumerate(players[:-1]):  #發明牌
          card1 = draw(player)
          card2 = draw(player)
          msg += f"{i+1}.{player.mention} : `{card1[0]}` `{card1[1]}`、`{card2[0]}` `{card2[1]}`\n"
        card1 = draw(players[-1])
        card2 = draw(players[-1])
        await initiator.send(f"暗牌：`{card1[0]}` `{card1[1]}`")
        msg += f"莊家：{players[-1].mention} :暗牌不公開、 `{card2[0]}` `{card2[1]}`"
        await channel.send(msg)
      await channel.send(f'現在是 {players[turn].mention} 的回合，輸入"`draw`"加牌，爆牌/21點/"`next`"結束加牌(遊戲)')

  @commands.command(aliases = ["BJ"])
  async def blackjack(self, ctx, n :int =2, r :int =1):
    global is_started
    global in_game
    global initiator
    global channel
    global participants
    global player_num
    global turn
    global t_round
    
    await ctx.message.delete()
    if is_started:
      await ctx.send("已經有人開始遊戲", delete_after = 3)
    else:
      if (not 1 < n <= 5) or (not 0 < r <= 5):
        await ctx.send("遊戲人數不合理或局數超出上限", delete_after = 3)
      else:
        turn = 0
        is_started = True
        in_game = False
        initiator = ctx.author
        channel = ctx.channel
        participants.setdefault(initiator , [0])
        player_num = n
        t_round = r
        await ctx.send(f'{ctx.author.mention}開始了21點遊戲，預計進行 **{r}** 回合\n輸入"`join`"以加入遊戲，參加人數達到 **{n}** 或遊戲發起人使用指令 `+BJ_s` 開始遊戲', delete_after = 60)

  @commands.Cog.listener()
  async def on_message(self, msg):
    global is_started
    global in_game
    global initiator
    global participants
    global channel
    global turn
    global players
    global player_num
    global Round

    if msg.content.lower() == "join" and is_started and not in_game and msg.channel == channel:
      await msg.delete()
      if msg.author in participants.keys():
        await msg.channel.send(f"{msg.author.mention}你已參加遊戲", delete_after = 3)
      else:
        participants.setdefault(msg.author, [0])
        players.append(msg.author)
        await msg.channel.send(f"{msg.author.mention}參加成功", delete_after = 3)
        if len(participants.keys()) == player_num:
          await BLACKJACK.game()

    elif in_game and msg.channel == channel and msg.author == players[turn]:
      if msg.content.lower() == "draw":  #加牌
        await msg.delete()
        card = draw(players[turn])
        await msg.channel.send(f"{msg.author.mention} : `{card[0]}` `{card[1]}`")
        player = participants[players[turn]]

        if player[0] > 21:     #爆牌
          MSG = ""
          #await msg.channel.send(f"{msg.author.mention} 爆牌了，手牌: {participants[players[turn]][1:]}，共 `{participants[players[turn]][0]}` 點")
          MSG += f"{msg.author.mention} 爆牌了，手牌:"
          for card in player[1:-1]:
            MSG += f"`{card[0]}` `{card[1]}`、"
          MSG += f"`{player[-1][0]}` `{player[-1][1]}`，共 `{player[0]}` 點"
          await msg.channel.send(MSG)
          del participants[players[turn]]

          if msg.author == initiator:  #莊家爆牌
            Round += 1
            await BLACKJACK.end_game()
          else:    #閒家爆牌
            turn += 1
            await BLACKJACK.game()
        '''else:   #21點
          if participants[players[turn]][0] == 21:
            await msg.channel.send(f"{msg.author.mention} 21點")
            turn += 1
            await BLACKJACK.game()'''

      elif msg.content.lower() == "next":  #結束加牌
        if msg.author == initiator:   #莊家
          Round += 1
          await BLACKJACK.end_game()
        else:   #閒家
          turn +=1
          await BLACKJACK.game()
        await msg.delete()

  @commands.command(aliases = ["p"])
  async def point(self, ctx):   #查詢點數
    global participants
    if is_started and in_game and ctx.author in participants.keys():
      await ctx.author.send(f"你的點數為： `{participants[ctx.author][0]} 點`")
    await ctx.message.delete()

  @commands.command()
  async def BJ_s(self, ctx):
    if is_started and not in_game and ctx.author == initiator:
      await BLACKJACK.game()
    else:
      await ctx.send("目前沒有遊戲可以開始或你不是遊戲發起人", delete_after = 5)
    await ctx.message.delete()
        

def setup(bot):
  bot.add_cog(BLACKJACK(bot))