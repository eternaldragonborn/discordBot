from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random
from wrFiles import readFile

url = readFile("others")

class Events(Cog_Ext):
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            if "rrrr" in msg.content or "啊啊啊啊" in msg.content:
                await msg.channel.send(f"{msg.author.mention}\n{url['rrr']}")
            elif msg.content.lower() == "loading cat":
                cat = str(random.choices(url["loadingCat"], weights= [3, 3, 1, 1])).strip("[]'")
                await msg.channel.send(cat)
            elif "虫合" in msg.content or "蛤" in msg.content:
                await msg.channel.send(random.choice(url["what"]), delete_after = 5)

    @commands.command()
    async def loading(self, ctx):
        cat = str(random.choices(url["loadingCat"], weights= [3, 3, 1, 1])).strip("[]'")
        await ctx.send(cat)

def setup(bot):
    bot.add_cog(Events(bot))