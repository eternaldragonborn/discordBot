import os
import re

from core import CogInit, Config, SQL_getData, SQL_modify
from discord.ext import commands
from redis import ConnectionPool, Redis

POOL = ConnectionPool(
    host=os.environ["REDIS_HOST"],
    port=15499,
    password=os.environ["REDIS_PASSWD"],
    decode_responses=True,
)
REDIS = Redis(connection_pool=POOL)

CHANNELS = Config.channel.book_info
EMOJI = "<:076:713997954201157723>"
EMOJI_ID = int(EMOJI[6:-1])


class Book(CogInit):
    @commands.command()
    async def book(self, ctx, url):
        await ctx.message.delete()
        if ctx.channel.id in CHANNELS and ctx.message.reference:
            if REDIS.sismember("msg_ids", ctx.message.reference.message_id):
                await ctx.send("該訊息已建檔過，更改網址請使用`+change_url 網址`", delete_after=5)
            else:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                await msg.add_reaction(EMOJI)
                REDIS.sadd("msg_ids", msg.id)
                SQL_modify(f"INSERT INTO book_url VALUES('{msg.id}', '{url}')")
                await ctx.send("建檔完畢，之後可使用`+check_user`取得獲取過該連結的人", delete_after=5)
        else:
            await ctx.send("頻道錯誤或沒有指定(reply)訊息")

    @commands.command()
    async def edit_url(self, ctx, url):
        await ctx.message.delete()
        if ctx.channel.id in CHANNELS and ctx.message.reference:
            if REDIS.sismember("msg_ids", ctx.message.reference.message_id):
                SQL_modify(
                    f"UPDATE book_url SET url='{url}' WHERE msg_id='{ctx.message.reference.message_id}'"
                )
                await ctx.send("更改完畢", delete_after=5)
            else:
                await ctx.send("該訊息尚未建檔，請使用`+upload_url 網址`進行建檔")
        else:
            await ctx.send("頻道錯誤或沒有指定(reply)訊息")

    @commands.command()
    async def get_user(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id in CHANNELS and ctx.message.reference:
            if REDIS.sismember("msg_ids", ctx.message.reference.message_id):
                users = SQL_getData(
                    "user_record", "msg_id", ctx.message.reference.message_id
                )  # ((msg_id, user_id))
                if users:
                    users = "\n".join(set(map(lambda x: x[1], users)))
                    await ctx.author.send(f"取得過該連結的使用者紀錄：\n{users}")
                else:
                    await ctx.author.send("無人取得過該連結")
            else:
                await ctx.send("該訊息尚未建檔，因此無取得連結的使用者紀錄")
        else:
            await ctx.send("頻道錯誤或沒有指定(reply)訊息")

    @commands.Cog.listener()  # 取得本子連結
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id in CHANNELS and not (payload.member.bot):
            if REDIS.sismember("msg_ids", payload.message_id) and payload.emoji.id == EMOJI_ID:
                url = SQL_getData("book_url", "msg_id", payload.message_id, 1)[1]
                try:
                    await payload.member.send(url)
                except:
                    await self.bot.get_channel(payload.channel_id).send(
                        payload.member.mention + "無法私訊連結給你，請檢查私訊設定"
                    )
                else:
                    try:
                        SQL_modify(
                            f"INSERT INTO user_record VALUES('{payload.message_id}', '<@{payload.user_id}>')"
                        )
                    except:
                        pass

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if reaction.message.channel.id in CHANNELS:
            if (
                REDIS.sismember("msg_ids", reaction.message.id)
                and str(reaction.emoji) == EMOJI
                and reaction.count == 0
            ):
                await reaction.message.add_reaction(EMOJI)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id in CHANNELS:
            if re.search(r"^[^+]*https?://([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?", msg.content):
                await msg.delete()
                await msg.channel.send(
                    msg.author.mention
                    + "為預防網址洩漏，請只貼出本本資訊及封面圖(如有)，並對該訊息進行回覆時使用指令`+upload_book 網址`進行建檔",
                    delete_after=10,
                )

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):  # 本子資訊刪除
        if payload.channel_id in CHANNELS:
            if REDIS.sismember("msg_ids", payload.message_id):
                REDIS.srem("msg_ids", payload.message_id)
                SQL_modify(f"DELETE FROM book_url WHERE msg_id='{payload.message_id}'")


def setup(bot):
    bot.add_cog(Book(bot))
