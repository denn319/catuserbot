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

# def file_handler (update, context):

#     if update.message['photo'] == []:
#         fileID = update.message['document']['file_id']
#         fileName = update.message['document']['file_name']
#         context.bot.sendDocument(chat_id = channel_chat_id,
#                                  caption = 'image caption',
#                                  document = fileID)

#     else:
#         fileID = update.message['photo'][-1]['file_id']
#         context.bot.sendPhoto(chat_id = channel_chat_id,
#                               caption = 'image caption',
#                               photo = fileID)

@catub.on(events.Album)
async def auto_fwd(e):
    if e.grouped_id:
        msg_id = get_message_id(e)
        await e.forward_to(TEST_CHANNEL_ID)       
        # catub.forward_messages(TEST_CHANNEL_ID, messages=events.Album)
        # LOGS.info(f"Message: {msg_id}")


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
