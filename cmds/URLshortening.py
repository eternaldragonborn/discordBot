from core.classes import Cog_Ext
import discord
from discord.ext import commands
import requests
from replit import db

headers = {
    'Content-Type': 'application/json',
    'reurl-api-key': f'{db["reurl_key"]}',
}

class URLshortening(Cog_Ext):
  
  @commands.command(aliases = ['URL_s'])
  async def URL_shorten(self, ctx, *urls):
    await ctx.message.delete()
    for url in urls:
      data = '{"url": '
      data += f'"{url}"'
      data += '}'
      r = requests.post('https://api.reurl.cc', headers=headers, data=data)
      if r.status_code in [requests.codes.ok, requests.codes.created]:
        await ctx.send(r.json())
      else:
        await ctx.send(f"發生錯誤，{r.status_code}", delete_after = 5)
        print(r.text)

def setup(bot):
  bot.add_cog(URLshortening(bot))