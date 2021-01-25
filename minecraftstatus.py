from mcrcon import MCRcon
from mcstatus import MinecraftServer
import logging
import time
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MinecraftStatus():
    def __init__(self, serverUrl, localIp, rconPort, queryPort, rconPassword):
        # FIXME is rconport used?
        self.serverUrl = serverUrl
        self.localServer = MinecraftServer(localIp, queryPort)
        self.urlServer = MinecraftServer(serverUrl, queryPort)
        self.rcon = MCRcon(localIp, rconPassword)
        self.previousPlayerAmountOnline = None

        try:
            self.rcon.connect()
        except ConnectionRefusedError:
            logger.error("RCON Connection refused")
        except:
            logger.error("Unexpected error while trying to connect to RCON")

    def generateStatus(self):
        tps = ""
        urlLatency = -1
        localLatency = -1
        playerAmountOnline = -1
        maxPlayerAmount = -1
        playerList = ""

        try:
            urlStatus = self.urlServer.status()
            urlLatency = str(urlStatus.latency)
        except:
            logger.error("Error while contacting server over url")

        try:
            localStatus = self.localServer.status()
            localLatency = str(localStatus.latency)
            playerAmountOnline = localStatus.players.online
            maxPlayerAmount = localStatus.players.max
            players = localStatus.players.sample
            if playerAmountOnline > 0:  # Quite hacky with the random dependency but ok
                for player in players:
                    playerList += player.name + ", "
                playerList = playerList[:-2]  # Remove last comma
                playerList += "."
        except:
            logger.error("Error while contacting server locally")

        try:
            tps = self.rcon.command("tps")
        except:
            logger.error("Rcon connection failed")
        tps = tps[29:]
        tps = tps.replace('§a', '')

        response = "```"
        response += 'Status report for ' + self.serverUrl + ': \n'
        if urlLatency != -1:
            response += "The server replied over DNS in " + \
                str(urlLatency) + 'ms\n'
        else:
            response += "The server did not reply over DNS\n"
        if localLatency != -1:
            response += "The server replied over the local network in " + \
                str(localLatency) + " ms\n"
            if playerAmountOnline > 0:
                response += "The server has " + \
                    str(playerAmountOnline) + "/" + \
                    str(maxPlayerAmount) + " players online.\n"
                response += "Online players: " + playerList + "\n"
            else:
                response += "No players are currently playing. Please do something about that :)\n"
            response += "The TPS for the server (1m,5m,15m) are: " + tps + "\n"
        else:
            response += "The server did not reply over the local network\n"
        response += "```"
        return response

    async def watch(self, sendNotifications):
        if self.previousPlayerAmountOnline is None:
            self.previousPlayerAmountOnline = self.localServer.status().players.online
            logger.debug("Initting prev players online")
        while True:  # FIXME?
            localStatus = self.localServer.status()
            playerAmountOnline = localStatus.players.online
            if playerAmountOnline != self.previousPlayerAmountOnline:
                logger.debug("Playercount changed!")
                self.previousPlayerAmountOnline = playerAmountOnline
                if playerAmountOnline == 1:
                    await sendNotifications("Someone started playing on the server :D")
                elif playerAmountOnline == 0:
                    await sendNotifications("Awh, the server is all empty now :(")
            await asyncio.sleep(0.0001)

    def say(self, message):
        try:
            self.rcon.command("say " + message)
        except BrokenPipeError:
            logger.error("No Pipe for RCON command")
