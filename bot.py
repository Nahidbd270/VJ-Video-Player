# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path
from datetime import date, datetime 
from aiohttp import web
from pyrogram import Client, idle 

# --- আপনার দেওয়া অন্যান্য ইম্পোর্ট ---
from info import *
from typing import Union, Optional, AsyncGenerator
from Script import script 
from plugins import web_server
from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# --- লগিং কনফিগারেশন (অপরিবর্তিত) ---
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


# --- প্লাগইন লোড করার জন্য একটি ফাংশন তৈরি করা হলো ---
def load_plugins():
    """Dynamically load all plugins from the 'plugins' directory."""
    ppath = "plugins/*.py"
    files = glob.glob(ppath)
    for name in files:
        try:
            with open(name) as a:
                patt = Path(a.name)
                plugin_name = patt.stem
                import_path = f"plugins.{plugin_name}"
                spec = importlib.util.spec_from_file_location(import_path, Path(f"plugins/{plugin_name}.py"))
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules[import_path] = load
                logging.info(f"Tech VJ Imported => {plugin_name}")
        except Exception as e:
            logging.error(f"Failed to load plugin {name}: {e}")


async def main():
    """
    Main function to initialize and start the bot.
    """
    logging.info("Initializing Your Bot...")
    
    # --- ক্লায়েন্ট এবং প্লাগইন ইনিশিয়ালাইজেশন ---
    # ক্লায়েন্টদের একসাথে শুরু করা হবে async context এর মধ্যে
    await TechVJBot.start()
    await TechVJBackUpBot.start()
    
    # অন্যান্য ক্লায়েন্ট ইনিশিয়ালাইজ করুন (যদি থাকে)
    await initialize_clients()
    
    # প্লাগইন লোড করুন
    load_plugins()

    # --- Heroku-র জন্য Keep-alive পিং সার্ভার ---
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # --- ওয়েব সার্ভার শুরু করুন ---
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    logging.info(f"Web server started on {bind_address}:{PORT}")

    # --- স্টার্টআপ মেসেজ পাঠান ---
    bot_info = await TechVJBot.get_me()
    logging.info(f"Bot @{bot_info.username} started successfully!")
    
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    try:
        await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    except Exception as e:
        logging.warning(f"Could not send restart message to LOG_CHANNEL: {e}")

    # --- বটকে সচল রাখুন ---
    await idle()

    # --- শাটডাউন প্রক্রিয়া ---
    logging.info("Stopping clients...")
    await TechVJBot.stop()
    await TechVJBackUpBot.stop()
    await app.cleanup() # ওয়েব সার্ভার বন্ধ করুন


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
    finally:
        # নিশ্চিত করুন যে লুপটি বন্ধ হয়েছে
        loop.close()
        logging.info("Event loop closed.")
