# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import Client, idle
from info import *
from typing import Union, Optional, AsyncGenerator
from Script import script
from datetime import date, datetime
from aiohttp import web
from plugins import web_server

from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)

# লুপ সম্পর্কিত লাইনটি সরিয়ে দেওয়া হয়েছে, কারণ asyncio.run() নিজেই লুপ পরিচালনা করবে
# TechVJBot.start() এবং TechVJBackUpBot.start() asynchronous হওয়া উচিত এবং start() এর ভেতর কল করা উচিত।
# যদি .start() সিনক্রোনাস হয়, তাহলে এখানে রাখতে পারেন।
# আপনার বর্তমান লগে এগুলো সিনক্রোনাস মনে হচ্ছে।

async def start():
    print('\n')
    print('Initalizing Your Bot')
    await TechVJBot.start() # এখানে .start() কে await করুন যদি এটি একটি async ফাংশন হয়
    await TechVJBackUpBot.start() # এখানে .start() কে await করুন যদি এটি একটি async ফাংশন হয়

    bot_info = await TechVJBot.get_me()
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    me = await TechVJBot.get_me()
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()


if __name__ == '__main__':
    try:
        # asyncio.run() ব্যবহার করুন যা একটি ইভেন্ট লুপ তৈরি ও পরিচালনা করে।
        asyncio.run(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')

