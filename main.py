import discordbot
import minecraftstatus

import sys
import os
import logging
import time
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Default settings
serverUrl = ""
localIp = '127.0.0.1'
queryPortString = 25565
rconPortString = 25575
rconPassword = ""
discordToken = ""
discordChannelName = ""
discordPrefix = ""

try:
    serverUrl = os.environ.get("SERVER_URL")

    discordToken = os.environ.get("DISCORD_TOKEN")

    localIp = os.environ.get("LOCAL_IP")
    queryPortString = os.environ.get("QUERY_PORT")
    rconPortString = os.environ.get("RCON_PORT")
    rconPassword = os.environ.get("RCON_PASSWORD")

    discordChannelName = os.environ.get("DISCORD_CHANNEL_NAME")
    discordPrefix = os.environ.get("DISCORD_PREFIX")
except:
    logger.critical("Parsing env vars failed. exiting.")
    sys.exit(1)

# Convert ports to integers
queryPort = int(queryPortString)
rconPort = int(rconPortString)

# Check obligatory settings
if serverUrl == "":
    logger.critical("No url given. exiting.")
    sys.exit(1)
if discordToken == "" or discordToken is None:
    logger.critical("No discord token given. exiting.")
    sys.exit(1)


def sayHi():
    print("HI")


async def main():
    mcstatus = minecraftstatus.MinecraftStatus(
        serverUrl, localIp, rconPort, queryPort, rconPassword)
    client = discordbot.MyClient(mcstatus.generateStatus, mcstatus.say)

    bot_future = client.start(discordToken)
    status_future = mcstatus.watch(client.notify)

    await asyncio.wait([bot_future, status_future])
    client.logout()
    logger.debug("Finished")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.set_debug(1)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.warning("Stopping")  # FIXME?
    finally:
        loop.close()
