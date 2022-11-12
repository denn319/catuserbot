import base64
import contextlib
from asyncio import sleep

from telethon.tl.functions.messages import *
from telethon.utils import *

from .. import catub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event
from ..sql_helper import broadcast_sql as sql
from . import BOTLOG, BOTLOG_CHATID

from telethon import events
from ..Config import Config

plugin_category = "tools"

LOGS = logging.getLogger(__name__)

SRC_CHANNEL_CAT = "source"  # can be any name. must exist using the .broadcast plug-in add command
DST_CHANNEL_CAT = "all"  # can be any name. must exist using the .broadcast plug-in add command

TEST_CHANNEL_ID = "-1001890495163"


class MyAlbum(events.Album):
    # def __int__(self, event):
    #     super().__init__(event)

    async def send_message(self, *args, **kwargs):
        """
        Sends the entire album. Shorthand for
        `telethon.client.messages.MessageMethods.send_message`
        with both ``messages`` and ``from_peer`` already set.
        """
        if self._client:
            kwargs['messages'] = self.messages
            kwargs['from_peer'] = await self.get_input_chat()
            return await self._client.send_message(*args, **kwargs)


myalbum = MyAlbum()


@catub.on(myalbum)
async def auto_albumfwd(e):
    channel_id = -100
    if e.grouped_id:
        keyword_src = SRC_CHANNEL_CAT
        no_of_sources = sql.num_broadcastlist_chat(keyword_src)
        if no_of_sources == 0:
            return
        sources = sql.get_chat_broadcastlist(keyword_src)

        if len(e.messages) > 1:
            channel_id = await e.messages[0].get_input_chat()

        LOGS.info(f"Sources: {sources}")
        LOGS.info(f"Channel ID: {channel_id}")

        #
        # # get destination
        # keyword = DST_CHANNEL_CAT
        # no_of_chats = sql.num_broadcastlist_chat(keyword)
        # if no_of_chats == 0:
        #     return
        # chats = sql.get_chat_broadcastlist(keyword)

        LOGS.info(str(await e.messages[0].get_input_chat()))
        LOGS.info(str(int(await e.messages[0].chat_id())))
        # await e.send_message(int(TEST_CHANNEL_ID))
        await e.forward_to(int(TEST_CHANNEL_ID))


async def autopost(event):
    """Auto-forward the message to all chats in the 'all' destination category."""
    # get source channels
    # load channels from the 'source' category
    keyword_src = SRC_CHANNEL_CAT
    no_of_sources = sql.num_broadcastlist_chat(keyword_src)
    if no_of_sources == 0:
        return
    sources = sql.get_chat_broadcastlist(keyword_src)
    source_valid = False
    for s in sources:
        if int(event.chat_id) == int(s):
            source_valid = True
    if not source_valid:
        return

    # get destination
    keyword = DST_CHANNEL_CAT
    no_of_chats = sql.num_broadcastlist_chat(keyword)
    if no_of_chats == 0:
        return
    chats = sql.get_chat_broadcastlist(keyword)
    i = 0
    for d in chats:
        try:
            if int(event.chat_id) == int(d):
                continue
            await catub.send_message(int(d), event.message)
            i += 1
        except Exception as e:
            LOGS.info(str(e))
        await sleep(0.5)
    ##

    if BOTLOG:
        await catub.send_message(
            BOTLOG_CHATID,
            f"A message is sent to {i} chats out of {no_of_chats} chats in category {keyword}",
            parse_mode=_format.parse_pre,
        )


# check if AUTOPOST config is set
if Config.AUTOPOST:
    if bool(Config.AUTOPOST and (Config.AUTOPOST.lower() != "false")):
        catub.add_event_handler(autopost, events.NewMessage())
