from core import CogInit
import requests, os, discord, re
from discord_slash.utils.manage_commands import create_option
from discord_slash import cog_ext
from discord.ext import commands
from cmds.redisDB import get_data, set_data

headers = {
    "Content-Type": "application/json",
    "reurl-api-key": f'{os.environ["REURL_KEY"]}',
}

urlPattern = re.compile(r"https?://([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?")

guildID = [719132687897591808, 669934356172636199]


def shorten(url):
    data = '{"url": "%s"}' % url
    return requests.post("https://api.reurl.cc/shorten", headers=headers, data=data)


class URLprocessing(CogInit):
    @cog_ext.cog_subcommand(
        base="url",
        name="shorten",
        description="縮短網址",
        options=[create_option(name="url", description="欲縮短的網址", option_type=3, required=True)],
    )
    async def URL_shorten(self, ctx, url):
        r = shorten(url)
        if r.ok:
            r = dict(r.json())
            await ctx.send(f'原網址：{url}\n短網址：{r["short_url"]}', hidden=True)
        else:
            await ctx.send(f"發生錯誤，{dict(r.json())['msg']}", hidden=True)

    async def store_url(self, ctx, urls: list):
        try:
            data = get_data(ctx.author.id)
        except:
            data = []
        finally:
            length = len(data)
            for url in urls:
                if url not in data:
                    data.append(url)
            set_data(ctx.author.id, data)
            await ctx.send(f"已儲存 `{len(data)-length}` 個網址", delete_after=3)

    @commands.command(aliases=["url_s", "save"])
    async def reply_to_save_url(self, ctx, num: int = None):
        urls = []
        await ctx.message.delete()
        if ctx.message.reference:
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if urlPattern.search(ref_msg.content):
                contents = re.split(r"[\n\s]", ref_msg.content)
                for content in contents:
                    r = urlPattern.search(content)
                    if r:
                        urls.append(r.group())
            elif ref_msg.attachments:
                if num:
                    urls.append(ref_msg.attachments[num].proxy_url)
                else:
                    for attachment in ref_msg.attachments:
                        urls.append(attachment.proxy_url)
        else:
            await ctx.send("這指令需reply一個有網址的訊息", delete_after=3)
        if urls:
            await self.store_url(ctx, urls)
        else:
            await ctx.send("reply的訊息中沒有網址或圖片", delete_after=3)

    @cog_ext.cog_subcommand(
        base="url",
        name="save",
        description="儲存網址",
        options=[create_option(name="url", description="要儲存的網址", option_type=3, required=True)],
    )
    async def url_saving(self, ctx, url):
        urls = []
        url = re.split(r"[\n\s]", url)
        for i in url:
            if urlPattern.search(i):
                urls.append(urlPattern.match(i).group())
        if len(urls) != 0:
            await self.store_url(ctx, urls)
        else:
            await ctx.send("參數中無任何網址", delete_after=3)

    @cog_ext.cog_subcommand(
        base="url",
        name="show",
        description="顯示儲存的網址",
        options=[create_option(name="user", description="指定使用者", option_type=6, required=False)],
    )
    async def url_show(self, ctx, user: discord.Member = None):
        if user and await self.bot.is_owner(ctx.author):
            target = user.id
        else:
            target = ctx.author.id

        try:
            urls = get_data(target)
        except Exception as e:
            await ctx.send("資料庫內沒儲存的網址", delete_after=3)
            print(e)
        else:
            msg = ""
            for i, url in enumerate(urls):
                if len(msg) + len(url) + len(str(i + 1)) + 2 > 2000:
                    await ctx.send(msg, hidden=True)
                    msg = ""
                msg += f"{i+1}. {url}\n"
            await ctx.send(msg, hidden=True)

    @cog_ext.cog_subcommand(
        base="url", name="count", description="顯示已存多少網址", options=[create_option("user", "指定使用者", 6, False)]
    )
    async def url_count(self, ctx, user: discord.Member = None):
        if user and await self.bot.is_owner(ctx.author):
            target = user.id
        else:
            target = ctx.author.id
        try:
            urls = get_data(target)
        except:
            await ctx.send("資料庫內沒儲存的網址", delete_after=3)
        else:
            await ctx.send(f"資料庫中有 `{len(urls)}` 條網址", hidden=True)

    @cog_ext.cog_subcommand(
        base="url",
        name="delete",
        description="清空/刪除儲存的網址",
        options=[
            create_option(name="start", description="要刪除的索引或連續的索引開頭", option_type=4, required=False),
            create_option(name="end", description="連續的索引結尾", option_type=4, required=False),
            create_option(name="user", description="指定使用者", option_type=6, required=False),
        ],
    )
    async def url_clear(self, ctx, user: discord.Member = None, start: int = None, end: int = None):
        if user and await self.bot.is_owner(ctx.author):
            target = user.id
        else:
            target = ctx.author.id
        try:
            get_data(target)
        except:
            await ctx.send("資料庫內沒儲存的網址", delete_after=3)
        else:
            if not start:
                set_data(target)
                await ctx.send("儲存的網址已清空", delete_after=3)
            else:
                urls = get_data(target)
                if not end:
                    del urls[start - 1]
                else:
                    del urls[start - 1 : end]
                set_data(target, urls)
                await ctx.send("指定網址已刪除", delete_after=3)

    @cog_ext.cog_subcommand(
        base="url",
        name="download",
        description="將網址存為檔案，並將資料庫清空",
        options=[create_option(name="user", description="指定使用者", option_type=6, required=False)],
    )
    async def url_download(self, ctx, user: discord.Member = None):
        if not user or not await self.bot.is_owner(ctx.author):
            user = ctx.author

        try:
            data = get_data(user.id)
        except:
            await ctx.send("無網址資料", delete_after=3)
        else:
            line = '{0}. <a href="{1}" target="_blank">{1}</a><br>\n'
            with open("urls.html", mode="w") as f:
                f.write(f"{user.name}儲存的網址<br>")
                for i, url in enumerate(data):
                    f.write(line.format(i, url))
            await ctx.send("檔案已發送至私訊", delete_after=3)
            await ctx.author.send("", file=discord.File("urls.html"))
            set_data(user.id)
            os.remove("urls.html")


def setup(bot):
    bot.add_cog(URLprocessing(bot))
