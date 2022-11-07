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

from telethon import events
from ..Config import Config

# https://github.com/Poolitzer/channelforwarder

from typing import TypedDict, List, Literal, cast

from telegram import Update, InputMediaVideo, InputMediaPhoto, InputMediaDocument, InputMediaAudio
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, Defaults, PicklePersistence
from telegram.utils.helpers import effective_message_type

plugin_category = "tools"

LOGS = logging.getLogger(__name__)

MEDIA_GROUP_TYPES = {"audio": InputMediaAudio, "document": InputMediaDocument, "photo": InputMediaPhoto,
                     "video": InputMediaVideo}

GROUP_ID = -1001818986606
CHANNEL_ID = -1001890495163

SRC_CHANNEL_CAT = "source"  # must exist using .broadcast command
DST_CHANNEL_CAT = "all"  # must exist duing .broadcast command


class MsgDict(TypedDict):
    media_type: Literal["video", "photo"]
    media_id: str
    caption: str
    post_id: int


def media_group_sender(context: CallbackContext):
    bot = context.bot
    context.job.context = cast(List[MsgDict], context.job.context)
    media = []
    for msg_dict in context.job.context:
        media.append(MEDIA_GROUP_TYPES[msg_dict["media_type"]](media=msg_dict["media_id"], caption=msg_dict["caption"]))
    if not media:
        return
    msgs = bot.send_media_group(chat_id=GROUP_ID, media=media)
    for index, msg in enumerate(msgs):
        context.bot_data["messages"][context.job.context[index]["post_id"]] = msg.message_id
    msgs[-1].pin()


def new_post(update: Update, context: CallbackContext):
    message = update.effective_message
    if message.media_group_id:
        media_type = effective_message_type(message)
        media_id = message.photo[-1].file_id if message.photo else message.effective_attachment.file_id
        msg_dict = {"media_type": media_type, "media_id": media_id, "caption": message.caption_html,
                    "post_id": message.message_id}
        jobs = context.job_queue.get_jobs_by_name(str(message.media_group_id))
        if jobs:
            jobs[0].context.append(msg_dict)
        else:
            context.job_queue.run_once(callback=media_group_sender, when=2, context=[msg_dict],
                                       name=str(message.media_group_id))
        return
    msg = message.copy(chat_id=GROUP_ID)
    context.bot.pin_chat_message(chat_id=GROUP_ID, message_id=msg.message_id)
    context.bot_data["messages"][message.message_id] = msg.message_id


def edited_post(update: Update, context: CallbackContext):
    message = update.effective_message
    msg_id = context.bot_data["messages"][message.message_id]
    bot = context.bot
    if message.text:
        bot.edit_message_text(chat_id=GROUP_ID, message_id=msg_id, text=message.text_html)
        return
    elif message.effective_attachment:
        media = None
        if message.location:
            bot.edit_message_live_location(chat_id=GROUP_ID, message_id=msg_id, **message.location.to_dict())
            return
        elif message.photo:
            media = InputMediaPhoto(media=message.photo[-1].file_id, caption=message.caption_html)
        elif message.video:
            media = InputMediaVideo(media=message.video.file_id, caption=message.caption_html)
        if not media:
            media = InputMediaDocument(media=message.effective_attachment.file_id, caption=message.caption_html)
        bot.edit_message_media(chat_id=GROUP_ID, message_id=msg_id, media=media)


def del_msg(update: Update, context: CallbackContext):
    if update.effective_user.id == context.bot.id:
        update.effective_message.delete()


def poll_msg():
    pers = PicklePersistence("persistence")
    defaults = Defaults(parse_mode="HTML", disable_notification=True)
    updater = Updater(Config.TG_BOT_TOKEN, defaults=defaults, persistence=pers)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.update.channel_post & Filters.chat(CHANNEL_ID), new_post))
    dp.add_handler(MessageHandler(Filters.update.edited_channel_post & Filters.chat(CHANNEL_ID), edited_post))
    dp.add_handler(MessageHandler(Filters.status_update.pinned_message & Filters.chat(GROUP_ID), del_msg))
    if "messages" not in dp.bot_data:
        dp.bot_data = {"messages": {}}
    updater.start_polling()
    updater.idle()


# async def autopost(event):
#     """Auto-forward the message to all chats in the 'all' destination category."""

    # get source channels
    # load channels from the 'source' category
    ###
    # keyword_src = "source"
    # no_of_sources = sql.num_broadcastlist_chat(keyword_src)
    # if no_of_sources == 0:
    #     return
    # sources = sql.get_chat_broadcastlist(keyword_src)
    #
    # source_valid = False
    # for s in sources:
    #     if int(event.chat_id) == int(s):
    #         source_valid = True
    # if not source_valid:
    #     return
    #
    # # get destination
    # keyword = "all"
    # no_of_chats = sql.num_broadcastlist_chat(keyword)
    # # if no_of_chats == 0:
    # #     return
    # chats = sql.get_chat_broadcastlist(keyword)
    # i = 0
    # for d in chats:
    #     try:
    #         if int(event.chat_id) == int(d):
    #             continue
    #
    #         await event.client.send_message(int(d), event.message)
    #
    #         i += 1
    #     except Exception as e:
    #         LOGS.info(str(e))
    #     await sleep(0.5)
    ###


    # if BOTLOG:
    #     await event.client.send_message(
    #         BOTLOG_CHATID,
    #         f"A message is sent to {i} chats out of {no_of_chats} chats in category {keyword}",
    #         parse_mode=_format.parse_pre,
    #     )


# check if AUTOPOST config is set
if Config.AUTOPOST:
    if bool(Config.AUTOPOST and (Config.AUTOPOST.lower() != "false")):
        catub.add_event_handler(MessageHandler(Filters.update.channel_post & Filters.chat(CHANNEL_ID), new_post))
