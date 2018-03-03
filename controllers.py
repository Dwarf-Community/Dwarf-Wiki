import asyncio

import aiohttp

from dwarf.core.controllers import CoreController
from dwarf.cache import Cache
from .models import Wiki


class WikiController:
    def __init__(self, bot=None):
        self.bot = bot
        self.loop = bot.loop if bot is not None else asyncio.get_event_loop()
        self.cache = Cache('wiki', bot=bot, loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.core = CoreController()

    def get_wiki(self, guild):
        try:
            return Wiki.objects.get(guild=self.core.get_guild(guild))
        except Wiki.DoesNotExist:
            return None

    def set_wiki(self, guild, wiki_root_url):
        wiki = Wiki(self.core.get_guild(guild))
        wiki.root = wiki_root_url
        wiki.save()
        return wiki

    def set_wikiprefix(self, prefix):
        return self.cache.set('prefix', prefix)

    def get_wikiprefix(self):
        return self.cache.get('prefix', '?')

    async def get_extracts(self, guild, title, *, characters=None, sentences=None,
                           limit=20, intro_only=False, page=None):
        if characters is not None and sentences is not None:
            raise TypeError("only one of characters and sentences can be passed")

        wiki = self.get_wiki(guild)

        params = {
            'action': 'query',
            'prop': 'extracts',
            'format': 'json',
            'titles': title,
            'explaintext': 1,
            'exsectionformat': 'plain'
        }
        if characters is not None:
            params['exchars'] = characters
        if sentences is not None:
            params['exsentences'] = sentences
        if limit != 20:
            params['exlimit'] = limit
        if intro_only:
            params['exintro'] = 1
        if page is not None:
            params['excontinue'] = page - 1

        async with self.session.get(wiki.api_url, params=params) as response:
            result = await response.json()

        try:
            return [extract['extract'] for extract in result['query']['pages'].values()]
        except KeyError:
            return None
