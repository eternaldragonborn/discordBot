from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random
from core.wrFiles import readFile
import re

url = readFile("others")


class Events(Cog_Ext):
	@commands.Cog.listener()
	async def on_message(self, msg):
		if msg.author != self.bot.user:
			if re.search(r'[啊阿ㄚ]{4,}', msg.content):
				await msg.channel.send(f"{msg.author.mention}\n{random.choice(url['rrr'])}",
				    delete_after=4)
			elif "loading cat" in msg.content.lower():
				cat = str(random.choices(url["loadingCat"],weights=[3, 3, 1, 1])).strip("[]'")
				await msg.channel.send(cat, delete_after=5)
			elif "星爆" in msg.content or "c8763" in msg.content.lower() or "starbust" in msg.content.lower():
				await msg.add_reaction("\N{THUMBS DOWN SIGN}")
			elif "虫合" in msg.content or "蛤" in msg.content:
				await msg.channel.send(random.choice(url["what"]), delete_after=5)

	'''@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		print(reaction)'''

	@commands.command()
	async def loading(self, ctx, delay_time: int = 5):
		cat = str(random.choices(url["loadingCat"], weights=[3, 3, 1, 1])).strip("[]'")
		await ctx.send(cat, delete_after=delay_time)
		await ctx.message.delete(delay=delay_time)


def setup(bot):
	bot.add_cog(Events(bot))
