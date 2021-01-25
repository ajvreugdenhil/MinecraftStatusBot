import discord
from mcrcon import MCRcon
from mcstatus import MinecraftServer
import sys
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    logger.critical("no url given. exiting.")
    sys.exit(1)
if discordToken == "" or discordToken is None:
    logger.critical("No discord token given. exiting.")
    sys.exit(1)

# Classes to pull data from
rcon = MCRcon(localIp, rconPassword)
try:
    rcon.connect()
except ConnectionRefusedError:
    logger.error("RCON Connection refused")
except:
    logger.error("Unexpected error while trying to connect to RCON")

localServer = MinecraftServer(localIp, queryPort)
urlServer = MinecraftServer(serverUrl, queryPort)

def generateStatus():
    tps = ""
    urlLatency = -1
    localLatency = -1
    playerAmountOnline = -1
    maxPlayerAmount = -1
    playerList = ""

    try:
        urlStatus = urlServer.status()
        urlLatency = str(urlStatus.latency)
    except:
        logger.error("Error while contacting server over url")

    try:
        localStatus = localServer.status()
        localLatency = str(localStatus.latency)
        playerAmountOnline = localStatus.players.online
        maxPlayerAmount = localStatus.players.max
        players = localStatus.players.sample
        if playerAmountOnline > 0: # Quite hacky with the random dependency but ok
            for player in players:
                playerList += player.name + ", "
            playerList = playerList[:-2] # Remove last comma
            playerList += "."
    except:
        logger.error("Error while contacting server locally")
    
    try:
        tps = rcon.command("tps")
    except:
        logger.error("Rcon connection failed")
    tps = tps[29:]
    tps = tps.replace('§a', '')

    response = "```"
    response += 'Status report for ' + serverUrl + ': \n'
    if urlLatency != -1:
        response += "The server replied over DNS in " + str(urlLatency) + 'ms\n'
    else:
        response += "The server did not reply over DNS\n"
    if localLatency != -1:
        response += "The server replied over the local network in " + str(localLatency) + " ms\n"
        if playerAmountOnline > 0:
            response += "The server has " + str(playerAmountOnline) + "/" + str(maxPlayerAmount) + " players online.\n"
            response += "Online players: " + playerList + "\n"
        else:
            response += "No players are currently playing. Please do something about that :)\n"
        response += "The TPS for the server (1m,5m,15m) are: " + tps + "\n"
    else:
        response += "The server did not reply over the local network\n"
    response += "```"
    return response


class MyClient(discord.Client):
    async def on_ready(self):
        logger.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        # Ignore all messages in irrelevant channels
        if not (message.channel.name == discordChannelName or discordChannelName == ""):
            return

        command = message.content.lower().split(" ")[0]
        if discordPrefix != "":
            command.replace(discordPrefix, "")

        if  (command == 'status'):
            logger.debug("Status command received")
            await message.channel.send('Hi! I\'m the mc status bot. Find me at github.com/ajvreugdenhil/MinecraftStatusBot')
            await message.channel.send(generateStatus())

        if  (command == 'say'):
            logger.debug("Send command received")
            if " " not in message.content:
                await message.channel.send("Send command requires 1 parameter")
                return
            messagebody = message.content.split(" ", 1)[1]
            sender = message.author.name
            try:
                rcon.command("say " + "<" + sender + "> " + messagebody)
            except BrokenPipeError:
                logger.error("No Pipe for RCON command")

client = MyClient()
client.run(discordToken)
