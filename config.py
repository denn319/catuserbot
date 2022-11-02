from sample_config import Config


class Development(Config):
    # get this values from the my.telegram.org
    APP_ID = 25944078
    API_HASH = "e353c491cc3c629bcf0203802111fdf9"
    # the name to display in your alive message
    ALIVE_NAME = "J Admin"
    # create any PostgreSQL database (i recommend to use elephantsql) and paste that link here
    DB_URI = "postgresql://postgres:7.tu53^7dBUse1B0tz@localhost:5432/catuserbot"
    # After cloning the repo and installing requirements do python3 stringsetup.py an fill that value with this
    STRING_SESSION = "1BVtsOGsBuyYbUwW6t13H0a3Vf5JQZdojP7xBxaVnQ76g8JoPEeRabYw6YM35zAqL5YtfiIazE6LjdPGwJu0nq0Wgb9GR3mU7XCqBPuTFBjKmoARetJFYY0O1ejfEkPMyHSrHmaImvVDP3DJfIXjZy6S-kZuDfBYv_2_sm-UXW9KDqHONhN5QTFuKlQO16Axy9VJswCo9WEzLI5VUCTVO9NftBHpyRmUDqNla2IBA9xORnQ3Ka6wAvEVywphF6BOiyKSiixRaZUcjVx4Ls_wc__0UGQDq8EcccLe_V-nfULilePuhbTRL79qYum3TqWwu3SR3mYXCJ4Le3iI3XDVRxKATDYG1iUQ="
    # create a new bot in @botfather and fill the following vales with bottoken
    TG_BOT_TOKEN = "5632822907:AAF1Ah3e4rd2YTJZiM8JpFr_UrVDM7WhM30" 
    # TG_BOT_TOKEN = "5632822907:AAH-qwkjineVI_SNa7QONfa0dThETrs-9Mw"
    # create a private group and a rose bot to it and type /id and paste that id here (replace that -100 with that group id)
    PRIVATE_GROUP_BOT_API_ID = -1001893401380
    # command handler
    COMMAND_HAND_LER = "."
    # command hanler for sudo
    SUDO_COMMAND_HAND_LER = "."
    # External plugins repo
    EXTERNAL_REPO = "https://github.com/TgCatUB/CatPlugins"
    # if you need badcat plugins set "True"
    BADCAT = "True"


    # API VARS FOR USERBOT
    # PM LOGGER GROUP ID
    PM_LOGGER_GROUP_ID = -1001893401380

    # Country
    COUNTRY = "Cambodia"
    TZ = "Asia/Phnom_Penh"
    
    # Personalized name for telegraph plugin
    TELEGRAPH_SHORT_NAME = "J News"

    # Get your own APPID from https://api.openweathermap.org/data/2.5/weather
    OPEN_WEATHER_MAP_APPID = "eacd362e5815d5e0354d41f54c9cd2b4"
    # Get your own ACCESS_KEY from http://api.screenshotlayer.com/api/capture for screen shot
    SCREEN_SHOT_LAYER_ACCESS_KEY = "0b1aec877725a8205f36a344c8a0c594"

    #CHROME DRIVERS
    CHROME_BIN = "/usr/bin/chromium-browser"
    CHROME_DRIVER = "/usr/bin/chromedriver"
