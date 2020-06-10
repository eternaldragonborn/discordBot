from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random
from wrFiles import readFile

state = 0
participants = []
initiator = 0
item = ""
winner_num = 0
winners = []
botId = readFile("setting")["botId"]

class Loot(Cog_Ext):
    @commands.command()
    async def loot(self, ctx, n :int, arg= ""):
        global state
        global participants
        global initiator
        global item
        global winner_num
        if state == 1:
            await ctx.send(f"已經有抽獎正在進行中，發起人：{self.bot.get_user(initiator).mention}", delete_after = 3)
        else:
            if n<=0:
                await ctx.send("無效的抽出人數", delete_after = 3)
            else:
                participants = []
                winner_num = n
                state = 1
                initiator = ctx.author.id
                item = arg
                await ctx.send(f"{ctx.author.mention} 開始了抽獎，預計抽出 ***{winner_num}*** 個人，輸入'**抽**'參加抽獎，指令'**loot_e**'抽出得獎人")
        await ctx.message.delete()

    @commands.command()
    async def loot_e(self, ctx):
        global initiator
        global item
        global participants
        global state
        global winner_num
        global winners
        if state == 0:
            await ctx.send("目前沒有抽獎", delete_after = 3)
        else:
            if ctx.author.id != initiator:
                await ctx.send("你不是抽獎發起人", delete_after = 3)
            else:
                await ctx.send(f"參加抽獎人數： {len(participants)}", delete_after = 5)
                if len(participants) < winner_num:
                    await ctx.send("參加人數少於預計抽出人數", delete_after = 5)
                else:
                    winners = random.sample(participants, winner_num)
                    await ctx.send("恭喜")
                    for i in winners:
                        await ctx.send(self.bot.get_user(i).mention)
                    await ctx.send(f"抽到了  {item}")
                state = 0
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, msg):
        global participants
        global initiator
        global state
        if msg.content == "抽" and state == 1 and msg.author.id != botId:
            if msg.author.id == initiator:
                await msg.channel.send(f"{self.bot.get_user(initiator).mention} 你不行抽你自己", delete_after = 4)
            elif msg.author.id in participants:
                await msg.channel.send(f"{msg.author.mention} 你已參加此抽獎", delete_after = 3)
            else:
                participants.append(msg.author.id)
                await msg.channel.send(f"{msg.author.mention} 參加成功", delete_after = 5)
            await msg.delete(delay = 3)

def setup(bot):
  bot.add_cog(Loot(bot))
