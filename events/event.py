from core.classes import Cog_Ext
import discord
from discord.ext import commands
import random
from core.wrFiles import readFile
import re


def choice_url(item):
	url = readFile("others")[item]
	return str(random.choices(list(url.keys()), weights = list(url.values()))).strip("[]'")

class Events(Cog_Ext):
	@commands.Cog.listener()
	async def on_message(self, msg):
		if msg.author != self.bot.user:
			if re.search(r'[rR啊阿ㄚ痾]{4,}', msg.content):
				await msg.channel.send(f"{msg.author.mention}\n{choice_url('rrr')}", delete_after=4)
			elif "loading cat" in msg.content.lower():
				await msg.channel.send(choice_url("loadingCat"), delete_after=5)
			elif re.search(r'(星爆)|(星暴)|(c8763)|(star(\s)?burst)', msg.content.lower()):
				await msg.add_reaction("\N{THUMBS DOWN SIGN}")
			elif "虫合" in msg.content or "蛤" in msg.content:
				await msg.channel.send(choice_url("what"), delete_after=5)
			elif re.match(r'emmm', msg.content.lower()):
				await msg.channel.send(choice_url("emmm"), delete_after = 5)

		'''@commands.Cog.listener()
		async def on_reaction_add(self, reaction, user):
			print(reaction)'''

	@commands.command()
	async def loading(self, ctx, delay_time: int = 5):
		await ctx.send(choice_url("loadingCat"), delete_after=delay_time)
		await ctx.message.delete(delay=delay_time)

	@commands.command()
	async def programming(self, ctx):
		await ctx.send(choice_url("programming"), delete_after = 4)
		await ctx.message.delete()


def setup(bot):
	bot.add_cog(Events(bot))
