import discord
from discord.ext import commands
from core.classes import Cog_Ext
from core.wrFiles import readFile
import random
import asyncio


is_started = False
in_game = False
initiator = ""  #莊家
participants = {}   #{name : [point, *cards]}
channel = ""  #遊玩的頻道
turn = 0
cards = []
players = []
point = readFile("cards")["point"]
player_num = 0


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
    maxpoint = 0 

    if len(participants.keys()) == 0:
      await channel.send("所有玩家皆爆牌，此局遊戲無贏家")
    else:
      for player, point in participants.items():
        if point[0] > maxpoint:    
          maxpoint = point[0]
          winner = player
      if winner == initiator:
        await channel.send(f"遊戲結束，莊家({initiator.mention})贏了")
      else:
        await channel.send(f"遊戲結束，{winner.mention}贏了")
      for player, point in participants.items():
        await channel.send(f"{player.mention} : {point[0]}點，手牌 : {point[1:]}")
    in_game = False
    is_started = False
    participants = {}
    players = []

  async def game():
    global in_game
    global is_started
    global players
    global initiator
    global cards
    global participants
    global turn

    if is_started and not in_game:
      if len(list(participants.keys())) <= 1:
        await channel.send("遊戲人數不足", delete_after = 5)
        is_started = False
        participants = []
      else:
        if turn == 0:  #遊戲開始
          cards = readFile("cards")["cards"]  #初始化牌組
          in_game = True
          random.shuffle(players)
          players.append(initiator)
          await channel.send("要牌順序及明牌：")
          for i, player in enumerate(players[:-1]):  #發明牌
            card = draw(player)
            await channel.send(f"{i+1}.{player.mention} : `{card[0]}` `{card[1]}`")
          card = draw(players[-1])
          await channel.send(f"莊家：{players[-1].mention} : `{card[0]}` `{card[1]}`")
    await channel.send(f'現在是 {players[turn].mention} 的回合，輸入"**draw**"加牌，"**next**"結束加牌(結束遊戲)')  #####?


  @commands.command()
  async def blackjack(self, ctx, n :int =2, round :int =1):
    global is_started
    global in_game
    global initiator
    global channel
    global participants
    global player_num
    global turn
    
    await ctx.message.delete()
    if is_started:
      await ctx.send("已經有人開始遊戲", delete_after = 3)
    else:
      if (not 1 < n < 5) or (not 0 < round <= 5):
        await ctx.send("遊戲人數不合理或局數超出上限", delete_after = 3)
      else:
        turn = 0
        is_started = True
        in_game = False
        initiator = ctx.author
        channel = ctx.channel
        participants.setdefault(initiator , [0])
        player_num = n
        await ctx.send(f"{ctx.author.mention}開始了21點遊戲，預計進行 **{round}** 回合", delete_after = 60)
        await ctx.send(f'輸入"***join***"以加入遊戲，60 秒後或參加人數達到 **{n}** 後開始遊戲', delete_after = 60)
        await asyncio.sleep(60)
        await BLACKJACK.game()


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

    if msg.content.lower() == "join" and is_started and not in_game and msg.channel == channel:
      if msg.author in participants.keys():
        await msg.channel.send(f"{msg.author.mention}你已參加遊戲", delete_after = 3)
      else:
        participants.setdefault(msg.author, [0])
        players.append(msg.author)
        await msg.channel.send(f"{msg.author.mention}參加成功", delete_after = 3)
        if len(participants.keys()) == player_num:
          await msg.channel.send("遊戲人數已滿")
          await BLACKJACK.game()
      

    elif in_game and msg.channel == channel and msg.author == players[turn]:
      if msg.content.lower() == "draw":  #加牌
        card = draw(players[turn])
        if msg.author == initiator:    #莊家(明牌)
          await msg.channel.send(f"{initiator.mention} : `{card[0]}` `{card[1]}`，共 `{participants[players[turn]][0]}` 點", delete_after = 5)
        else:    #閒家(暗牌)
          await msg.author.send(f"`{card[0]}` `{card[1]}`，目前共 `{participants[players[turn]][0]}` 點")

        if participants[players[turn]][0] > 21:     #爆牌
          await msg.channel.send(f"{msg.author.mention} 爆牌了，手牌: {participants[players[turn]][1:]}，共 `{participants[players[turn]][0]}` 點", delete_after = 7)
          del participants[players[turn]]
          print(participants)

          if msg.author == initiator:  #莊家爆牌
            await BLACKJACK.end_game()
          else:    #閒家爆牌
            turn += 1
            await BLACKJACK.game()

      elif msg.content.lower() == "next":  #結束加牌
        if msg.author == initiator:   #莊家
          await BLACKJACK.end_game()
        else:   #閒家
          turn +=1
          await BLACKJACK.game()
      await msg.delete()
        

def setup(bot):
  bot.add_cog(BLACKJACK(bot))