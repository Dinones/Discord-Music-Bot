###########################################################################################################################
#   Implements the !stats command, which renders the dashboard and sends a screenshot to the Discord channel.             #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import io
import os
import sys
import asyncio
import discord
from discord.ext import commands

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Colored_Strings as STR
from Utils.Reactions import send_reaction
from Utils.Logs import save_exception_to_txt

try:
    from Utils import Custom_Messages as MSG
except:
    from Utils import Messages as MSG

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

_VIEWPORT_WIDTH = 1800
_SCALE          = 2

###########################################################################################################################
###########################################################################################################################

def _render_and_screenshot() -> bytes:

    """
    Render the dashboard template in-memory using Flask's app context, then feed the resulting HTML to a
    headless Chromium browser and return a full-page PNG screenshot as bytes. No running server required.
    """

    from flask import render_template
    from Dashboard.app import app as flask_app, _load_stats
    from playwright.sync_api import sync_playwright

    with flask_app.app_context():
        html = render_template("index.html", **_load_stats())

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page    = browser.new_page(
            viewport           = {"width": _VIEWPORT_WIDTH, "height": 900},
            device_scale_factor = _SCALE,
        )
        page.set_content(html, wait_until = "networkidle")
        page.wait_for_timeout(600)
        height = page.evaluate("document.body.scrollHeight")
        page.set_viewport_size({"width": _VIEWPORT_WIDTH, "height": height})
        screenshot = page.screenshot()
        browser.close()

    return screenshot

###########################################################################################################################
#################################################     COMMANDS     ########################################################
###########################################################################################################################

def register_stats_command(bot: commands.Bot) -> None:

    """
    Register the "!stats" command.

    Args:
        bot (commands.Bot): Bot instance where the command will be attached.
    """

    @bot.command(name = "stats")
    async def stats_command(context: commands.Context) -> None:

        """
        Render the stats dashboard and post a screenshot in the channel.
        """

        await send_reaction(context.message, "⏳")

        async with context.typing():
            try:
                screenshot_bytes = await asyncio.to_thread(_render_and_screenshot)
            except Exception as error:
                print(
                    STR.G_ACTION_NOT_DONE.format(
                        user   = context.author.name.capitalize(),
                        action = "generate stats screenshot",
                        reason = error
                    )
                )
                save_exception_to_txt(error = error, title = 'Stats_Screenshot')
                await context.message.remove_reaction("⏳", context.bot.user)
                await send_reaction(context.message, "❌")
                await context.send(MSG.STATS_GENERATION_FAILED)
                return

        await context.message.remove_reaction("⏳", context.bot.user)

        file = discord.File(io.BytesIO(screenshot_bytes), filename = "stats.png")
        await context.send(file = file)

        print(
            STR.G_ACTION_DONE.format(
                user   = context.author.name.capitalize(),
                action = "generate stats screenshot",
                result = "Screenshot sent to Discord"
            )
        )
        await send_reaction(context.message, "✅")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
