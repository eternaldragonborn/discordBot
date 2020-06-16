import discord
from discord.ext import commands
from core.classes import Cog_Ext

import unicodedata

class Emo_search(Cog_Ext):
    @commands.command(aliases= ["Emoji", "Emo", "Unicode", "Uni"])
    async def Emo_search(self, ctx, *,E_input):
        if E_input.startswith(":") and E_input.endswith(":"):
            E_input = E_input.strip(":")
        try:
            Emoji = await commands.EmojiConverter().convert(ctx, E_input)
        except:
            try:
                Name = unicodedata.name(E_input)
            except:
                await ctx.send("Input Error!")
            else:
                await ctx.send(f"{E_input} {Name}")
        else:
            if Emoji.animated:
                await ctx.send(f"\<a:{Emoji.name}:{Emoji.id}>")
            else:
                await ctx.send(f"\<:{Emoji.name}:{Emoji.id}>")
        await ctx.message.delete(delay= 3)

def setup(bot):
    bot.add_cog(Emo_search(bot))