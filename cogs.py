import discord
from discord.ext import commands
from django.utils.http import urlquote

from dwarf.bot import Cog
from dwarf import checks
from .controllers import WikiController


class Core(Cog):
    """All commands that relate to management operations."""

    def __init__(self, bot, extension):
        super().__init__(bot, extension)
        self.wiki = WikiController(bot=bot)

    @commands.command()
    @commands.is_owner()
    async def set_wikiprefix(self, ctx, prefix):
        self.wiki.set_wikiprefix(prefix)
        await ctx.send("The Wiki prefix has been set to **{0}**. Search the wiki of this server like this: "
                       "`{0}<search term>`".format(prefix))

    @commands.command()
    @checks.is_guild_owner()
    async def set_wiki(self, ctx, url):
        self.wiki.set_wiki(ctx.guild, url)
        await ctx.send("The root URL for this server's Wiki has been set.")

    async def on_message(self, message):
        prefix = self.wiki.get_wikiprefix()
        if not message.content.startswith(prefix):
            return

        wiki = self.wiki.get_wiki(message.guild)
        if wiki is None:
            return

        search_term = message.content.split(prefix, 1)[1]
        extract = await self.wiki.get_extracts(message.guild, search_term, characters=480, intro_only=True)
        if extract is None:
            await message.channel.send("I could not find anything for **{}**.".format(search_term))
            return
        url = wiki.article_url + urlquote(search_term)
        embed = discord.Embed(title=search_term, url=url, description=extract[0])
        await message.channel.send(embed=embed)
