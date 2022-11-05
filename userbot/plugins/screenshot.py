"""
`Credits` @amnd33p
from ..helpers.utils import _format
Modified by @mrconfused
"""

import io
import traceback
from datetime import datetime

import requests
from selenium import webdriver
from validators.url import url

from userbot import catub

from ..Config import Config
from ..core.managers import edit_or_reply
from . import reply_id

# denn319
from selenium.webdriver.common.by import By
from PIL import Image

plugin_category = "utils"


@catub.cat_cmd(
    pattern="(ss|gis|gw) ([\s\S]*)",
    command=("ss", plugin_category),
    info={
        "header": "To take a screenshot of a website or get a weather snapshot from Google.",
        "description": "It runs the query and returns the screenshot",
        "usage": [
            "{tr}ss <link>",
            "{tr}gis <query>",
            "{tr}gw <City name>",
        ],
        "examples": [
            "{tr}ss https://github.com/denn319/catuserbot",
            "{tr}gis cat",
            "{tr}gw Phnom Penh [wind | precipitation]",
        ],
    },
)
async def _(event):
    "To take a screenshot of a website."
    if Config.CHROME_BIN is None:
        return await edit_or_reply(
            event, "Need to install Google Chrome. Module Stopping."
        )
    catevent = await edit_or_reply(event, "`Processing ...`")
    start = datetime.now()
    try:
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--test-type")
        chrome_options.add_argument("--headless")
        # https://stackoverflow.com/a/53073789/4723940
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = Config.CHROME_BIN
        await event.edit("`Starting Google Chrome BIN`")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        
        cmd = event.pattern_match.group(1)
        input_str = event.pattern_match.group(2)
        inputstr = input_str
        
        if cmd == "ss":
            caturl = url(inputstr)
            if not caturl:
                inputstr = f"http://{input_str}"
                caturl = url(inputstr)
            if not caturl:
                return await catevent.edit("`The given input is not supported url`")
        if cmd == "gis":
            inputstr = f"https://www.google.com/search?q={input_str}"
        if cmd == "gw":
            inputstr = f"https://www.google.com/search?q=weather+{input_str}"
        
        driver.get(inputstr)
        await catevent.edit("`Calculating Page Dimensions`")
            
        if cmd == "ss" or cmd == "gis":                
            height = driver.execute_script(
                "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
            )
            width = driver.execute_script(
                "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
            )
            driver.set_window_size(width + 100, height + 100)
            # Add some pixels on top of the calculated dimensions
            # for good measure to make the scroll bars disappear
        
        # denn319 test get weather out from google.com
        if cmd == "gw":
      
            # find part of the page we want image from an element id
            element = driver.find_element(By.ID, 'wob_wc')
            location = element.location
            size = element.size
            # saves screenshot of entire page
            png = driver.get_screenshot_as_png()

            im = Image.open(io.BytesIO(png)) # uses PIL library to open image in memory
            
            left = location['x'] - 10
            top = location['y'] - 10
            right = location['x'] + size['width'] + 10
            bottom = location['y'] + size['height'] + 10

            cim = im.crop((left, top, right, bottom)) # defines crop points
            cim_bytes = io.BytesIO()
            cim.save(cim_bytes, format="png")
            im_png = cim_bytes.getvalue()
            
        else:
            im_png = driver.get_screenshot_as_png()
            # saves screenshot of entire page
        
        await catevent.edit("`Stopping Chrome Bin`")
        driver.close()
        message_id = await reply_id(event)
        end = datetime.now()
        ms = (end - start).seconds
        hmm = f"**cmd : **{cmd} \n**Time :** `{ms} seconds`"
        await catevent.delete()
        
        with io.BytesIO(im_png) as out_file:
            out_file.name = f"{cmd}.png"
            await event.client.send_file(
                event.chat_id,
                out_file,
                caption=hmm,
                # force_document=True, #do NOT send as file
                reply_to=message_id,
                allow_cache=False,
                silent=True,
            )
    except Exception:
        await catevent.edit(f"`{traceback.format_exc()}`")


@catub.cat_cmd(
    pattern="scapture ([\s\S]*)",
    command=("scapture", plugin_category),
    info={
        "header": "To Take a screenshot of a website.",
        "description": "For functioning of this command you need to set SCREEN_SHOT_LAYER_ACCESS_KEY var",
        "usage": "{tr}scapture <link>",
        "examples": "{tr}scapture https://github.com/TgCatUB/catuserbot",
    },
)
async def _(event):
    "To Take a screenshot of a website."
    start = datetime.now()
    message_id = await reply_id(event)
    if Config.SCREEN_SHOT_LAYER_ACCESS_KEY is None:
        return await edit_or_reply(
            event,
            "`Need to get an API key from https://screenshotlayer.com/product and need to set it SCREEN_SHOT_LAYER_ACCESS_KEY !`",
        )
    catevent = await edit_or_reply(event, "`Processing ...`")
    sample_url = "https://api.screenshotlayer.com/api/capture?access_key={}&url={}&fullpage={}&viewport={}&format={}&force={}"
    input_str = event.pattern_match.group(1)
    inputstr = input_str
    caturl = url(inputstr)
    if not caturl:
        inputstr = f"http://{input_str}"
        caturl = url(inputstr)
    if not caturl:
        return await catevent.edit("`The given input is not supported url`")
    response_api = requests.get(
        sample_url.format(
            Config.SCREEN_SHOT_LAYER_ACCESS_KEY, inputstr, "1", "2560x1440", "PNG", "1"
        )
    )
    # https://stackoverflow.com/a/23718458/4723940
    contentType = response_api.headers["content-type"]
    end = datetime.now()
    ms = (end - start).seconds
    hmm = f"**url : **{input_str} \n**Time :** `{ms} seconds`"
    if "image" in contentType:
        with io.BytesIO(response_api.content) as screenshot_image:
            screenshot_image.name = "screencapture.png"
            try:
                await event.client.send_file(
                    event.chat_id,
                    screenshot_image,
                    caption=hmm,
                    force_document=True,
                    reply_to=message_id,
                )
                await catevent.delete()
            except Exception as e:
                await catevent.edit(str(e))
    else:
        await catevent.edit(f"`{response_api.text}`")
