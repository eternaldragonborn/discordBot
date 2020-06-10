from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random

state = 0
participants = []
initiator = 0
item = ""
winner_num = 0
winners = []

class Loot(Cog_Ext):
    @commands.command()
    async def loot_s(self, ctx, n :int, arg= ""):
        global state
        global participants
        global initiator
        global item
        global winner_num
        if state == 1:
            await channel.send(f"{self.bot.get_user(initiator).mention}已經發起抽獎")
        else:
            if n<=0:
                await channel.send("無效的抽出人數")
            else:
                participants = []
                winner_num = n
                state = 1
                initiator = ctx.author.id
                item = arg
                await channel.send(f"{ctx.author.mention}開始了抽獎，預計抽出{winner_num}個人，輸入'抽'參加抽獎，指令'loot_e'抽出得獎人")

    @commands.command()
    async def loot_e(self, ctx):
        global initiator
        global item
        global participants
        global state
        global winner_num
        global winners
        if state == 0:
            await channel.send("目前沒有抽獎")
        else:
            if ctx.author.id != initiator:
                await channel.send("你不是抽獎發起人")
            else:
                if len(participants) <= winner_num:
                    await channel.send("參加人數少於預計抽出人數")
                else:
                    winners = []
                    for i in range(winner_num):
                        winner = random.choice(participants)
                        winners.append(winner)
                        participants.remove(winner)
                    await channel.send("恭喜")
                    for i in winners:
                        await channel.send(self.bot.get_user(i).mention)
                    await channel.send(f"抽到了{item}")
                state = 0

    @commands.Cog.listener()
    async def join_loot(self, msg):
        global participants
        global initiator
        global state
        if msg.content == "抽" and state == 1 and msg.author != self.bot.user:
            if msg.author == initiator:
                await msg.channel.send(f"{self.bot.get_user(initiator).mention} 你不行抽你自己")
            else:
                participants.append(msg.author.id)
