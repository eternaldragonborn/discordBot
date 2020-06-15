import discord
from discord.ext import commands
from core.classes import Cog_Ext
from core.wrFiles import readFile
import random


is_started = False    #declear, lots of declear
in_game = False
initiator = ""  #莊家
participants = {}   #{name : [point, *cards]}  ->  {name : [*cards]}
channel = ""  #遊玩的頻道
turn = 0
cards = []
players = []
point = readFile("cards")["point"]
player_num = 0
Round = 1
t_round = 0
join_message_id = 0


def draw(player):  #抽牌
  global cards
  global point
  global participants
  random.shuffle(cards)
  card = cards.pop()    #考慮以random產生index
  participants[player].append(card)
  return card

def point_check(player):
  global participants
  global point
  total_p = 0
  p = []
  ace_count = 0
  for card in participants[player]:
    if card[1] == "A":
      ace_count += 1
    else:
      total_p += point[card[1]]
  if ace_count == 0:  #無Ace
    return [total_p]
  else:
    for i in range(1, ace_count+1):
      temp = total_p + i + 11*(ace_count-i)
      if temp < 21 and temp not in p:
        p.append(temp)

      temp = total_p + 11*i + (ace_count-i)
      if temp < 21 and temp not in p:
        p.append(temp)

      if (total_p + i + 11*(ace_count-i)) == 21 or (total_p + 11*i + (ace_count-i)) == 21:
        p = [21]
        break
      if p == []:  #不符合前面任何條件(爆牌)
        p = [total_p + i + 11*(ace_count-i)]
      else:
        break
    return p


class BLACKJACK(Cog_Ext):

  async def end_game():
    global participants
    global channel
    global in_game
    global is_started
    global players
    global Round
    global turn

    if len(participants.keys()) == 0:
      await channel.send("所有玩家皆爆牌，此局遊戲無贏家")
    else:
      point = []
      winner = []
      msg = ""
      for player in participants.keys():
        point.append(max(point_check(player)))
      for i, player in enumerate(participants.keys()):
        if point[i] == max(point):    
          winner.append(player)
      if initiator in winner:
        msg += f"回合結束，莊家({initiator.mention})"
      else:
        msg += "回合結束，"
        for player in winner:
          if player != winner[-1]:
            msg += f" {player.mention} &"
          else:
            msg += f" {player.mention}"
      msg += "贏了，各玩家資訊：\n"
      for player, p in zip(list(participants.items()), point):
        msg += f"{player[0].mention} : `{p}` 點，手牌 :"
        for card in player[1]:
          if card != player[1][-1]:
            msg += f"`{card[0]}` `{card[1]}`、"
          else:
            msg += f"`{card[0]}` `{card[1]}`\n"
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
      participants = {initiator : []}
      players.remove(initiator)
      for player in players:
        participants.setdefault(player , [])
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
        await channel.send("遊戲開始，由於bot一定時間內只能發5則訊息，若訊息卡住請稍待數秒")
        in_game = True
    if is_started and in_game:
      if turn == 0:  #回合開始
        cards = readFile("cards")["cards"]  #初始化牌組
        random.shuffle(players)
        players.append(initiator)
        await channel.send(f"第 {Round} 回合開始，要牌順序及明牌：")
        msg = ""
        for i, player in enumerate(players):  #發明牌
          card1 = draw(player)
          card2 = draw(player)
          if player != players[-1]:
            msg += f"{i+1}.{player.mention} : `{card1[0]}` `{card1[1]}`、`{card2[0]}` `{card2[1]}`\n"
          else:
            await initiator.send(f"暗牌：`{card1[0]}` `{card1[1]}`")
            msg += f"莊家：{player.mention} : `暗牌不公開`、`{card2[0]}` `{card2[1]}`"
        await channel.send(msg)
      await channel.send(f'現在是 {players[turn].mention} 的回合，輸入"`draw`"加牌，爆牌/21點/"`next`"結束加牌(遊戲)，`+p` 查詢點數')

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
    global join_message_id
    
    await ctx.message.delete()
    if is_started:
      await ctx.send("已經有人開始遊戲", delete_after = 3)
    else:
      if (not 1 < n <= 10) or (not 0 < r <= 5):
        await ctx.send("遊戲人數或局數不合理(1 < 人數 <= 10， 0 < 局數 <= 5)", delete_after = 3)
      else:
        turn = 0
        is_started = True
        in_game = False
        initiator = ctx.author
        channel = ctx.channel
        participants.setdefault(initiator , [])
        player_num = n
        t_round = r
        msg = await ctx.send(f'{ctx.author.mention}開始了21點遊戲，預計進行 **{r}** 回合\n選取\N{WHITE HEAVY CHECK MARK}或輸入 `join` 參加遊戲，加入後選取\N{NEGATIVE SQUARED CROSS MARK}可退出，參加人數達到 **{n}** 或遊戲發起人使用指令 `+BJ_s` 時開始遊戲')
        join_message_id = msg.id
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")

  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    global join_message_id
    global participants
    global players
    global channel
    if user != self.bot.user and reaction.message.id == join_message_id and is_started and not in_game:
      await reaction.remove(user)
      if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}":
        if user not in participants.keys():
          participants.setdefault(user, [])
          players.append(user)
          await channel.send(f"{user.mention}參加成功", delete_after = 3)
          if len(participants.keys()) == player_num:
            await BLACKJACK.game()
        else:
          await channel.send(f"{user.mention}你已在遊戲中", delete_after = 3)
      elif str(reaction.emoji) == "\N{NEGATIVE SQUARED CROSS MARK}":
        if user in participants.keys():
          del participants[user]
          players.remove(user)
          await channel.send(f"{user.mention}取消參加成功", delete_after = 3)
        else:
          await channel.send(f"{user.mention}你沒有在遊戲中", delete_after = 3)
        

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
        participants.setdefault(msg.author , [])
        players.append(msg.author)
        await msg.channel.send(f"{msg.author.mention}參加成功", delete_after = 3)
        if len(participants.keys()) == player_num:
          await BLACKJACK.game()

    elif in_game and msg.channel == channel and msg.author == players[turn]:
      if msg.content.lower() == "draw":  #加牌
        await msg.delete()
        card = draw(players[turn])
        await msg.channel.send(f"{msg.author.mention} : `{card[0]}` `{card[1]}`")
        player = players[turn]
        point = point_check(player)

        if len(point) == 1 and point[0] > 21:     #爆牌
          MSG = f"{msg.author.mention} 爆牌了，手牌:"
          for card in participants[player]:
            if card != participants[player][-1]:
              MSG += f"`{card[0]}` `{card[1]}`、"
            else:
              MSG += f"`{card[0]}` `{card[1]}`，共 `{point[0]}` 點"
          await msg.channel.send(MSG)
          del participants[player]

          if msg.author == initiator:  #莊家爆牌
            Round += 1
            await BLACKJACK.end_game()
          else:    #閒家爆牌
            turn += 1
            await BLACKJACK.game()
        elif point == [21]:   #21點
          await msg.channel.send(f"{msg.author.mention} 21點")
          if msg.author == initiator:  #莊家
            Round += 1
            await BLACKJACK.end_game()
          else:   #閒家
            turn += 1
            await BLACKJACK.game()

      elif msg.content.lower() == "next":  #結束加牌
        if msg.author == initiator:   #莊家
          Round += 1
          await BLACKJACK.end_game()
        else:   #閒家
          turn +=1
          await BLACKJACK.game()
        await msg.delete()

  @commands.command()
  async def p(self, ctx):   #查詢點數
    global participants
    if is_started and in_game and ctx.author in participants.keys() and ctx.channel == channel:
      point = point_check(ctx.author)
      msg = "你的點數可為： "
      for p in point:
        if p != point[-1]:
          msg += f" `{p}` "
        else:
          msg += (f" `{p}` 點")
      await ctx.author.send(msg)
    await ctx.message.delete()

  @commands.command()
  async def BJ_s(self, ctx):
    if is_started and not in_game and ctx.author == initiator:
      await BLACKJACK.game()
    else:
      await ctx.send("目前沒有遊戲可以開始或你不是遊戲發起人", delete_after = 5)
    await ctx.message.delete()

  @commands.command()
  async def BJ_e(self, ctx):
    global in_game
    global is_started
    global participants
    global players
    global Round
    if is_started and in_game and ctx.author == initiator:
      await ctx.send("強制結束遊戲成功", delete_after = 3)
      in_game = False
      is_started = False
      participants = {}
      players = []
      Round = 1
    else:
      await ctx.send("目前沒有遊戲正在進行或你不是遊戲發起人", delete_after = 5)
    await ctx.message.delete()
        

def setup(bot):
  bot.add_cog(BLACKJACK(bot))