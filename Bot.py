from discord.ext import commands
from typing import Pattern
import discord
import re

import Logging
import cogs.Utils as Utils

# Loads the configuration file.
config: dict = Utils.loadConfig("Bot")
name: str = config["name"]
isSelfBot: bool = config["isSelfBot"]

bot: commands.Bot = commands.Bot(command_prefix = config["prefixes"],
                                 description = name,
                                 self_bot = isSelfBot,
                                 pm_help = None,
                                 help_attrs = dict(hidden = True))

@bot.event
async def on_ready():
    log.info(f"{name} logged in as {bot.user} ({bot.user.id})")

@bot.event
async def on_resumed():
    log.info(f"{name} resumed.")

@bot.event
async def on_message(msg: discord.Message):
    # Ignores direct/private messages.
    if msg.server is None:
        return

    # Only processes commands if called by users as specified in the config.
    if msg.author.id in config["idUsers"]:
        await bot.process_commands(msg)

if __name__ == "__main__":
    # Creates loggers.
    strFormat: str = "%(asctime)s - [%(levelname)s] %(name)s: %(message)s"
    pattern: Pattern = re.compile(r"Unhandled event", re.IGNORECASE)
    handler: Logging.StreamFiltered = Logging.StreamFiltered(pattern)

    loggerBot: Logging.Logger = Logging.Logger("bot", strFormat)
    loggerDiscord: Logging.Logger = Logging.Logger("discord", strFormat, handler)
    log = loggerBot.log

    # Loads extensions.
    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error(f"{extension} failed to load.\n"
                      f"{type(e).__name__}: {e}")

    bot.run(config["token"], bot = not isSelfBot) # Starts the bot.

    # Closes and removes logging handlers.
    loggerBot.close()
    loggerDiscord.close()
