import base64
import contextlib
from asyncio import sleep

from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.utils import get_display_name

from .. import catub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event
from ..sql_helper import broadcast_sql as sql
from . import BOTLOG, BOTLOG_CHATID

from ..Config import Config

plugin_category = "tools"

LOGS = logging.getLogger(__name__)


async def autopost(event):
    """Auto-forward the message to all chats in the 'all' destination category."""

    # get source channels
    # load channels from the 'source' category
    keyword_src = "source"
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
    keyword = "all"
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
        catub.add_event_handler(autopost)
