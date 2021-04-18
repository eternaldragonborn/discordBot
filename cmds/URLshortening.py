from core.classes import Cog_Ext
import requests
from discord_slash.utils.manage_commands import create_option
from discord_slash import cog_ext
from replit import db

headers = {
    'Content-Type': 'application/json',
    'reurl-api-key': f'{db["reurl_key"]}',
}

class URLshortening(Cog_Ext):
  
  @cog_ext.cog_slash(name='urlshorten', description='縮短網址', options=[
                    create_option(name='url', description='欲縮短的網址', option_type=3, required=True)
                    ])
  async def URL_shorten(self, ctx, url):
    data = '{"url": '
    data += f'"{url}"'
    data += '}'
    r = requests.post('https://api.reurl.cc/shorten', headers=headers, data=data)
    if r.ok:
      r = dict(r.json())
      await ctx.send(f'原網址：{url}\n短網址：{r["short_url"]}', hidden=True)
    else:
      await ctx.send(f"發生錯誤，{r.reason}", hidden=True)

def setup(bot):
  bot.add_cog(URLshortening(bot))