from mcrcon import MCRcon
from mcstatus import JavaServer
import logging
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MinecraftStatus():
    def __init__(self, serverUrl, localIp, rconPort, queryPort, rconPassword):
        self.serverUrl = serverUrl
        self.localServer = JavaServer.lookup(localIp, queryPort)
        self.urlServer = JavaServer.lookup(serverUrl, queryPort)
        self.rcon = MCRcon(localIp, rconPassword, port=rconPort)
        self.previousPlayerAmountOnline = None
        self.rconConnect()

    def rconConnect(self):
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
        mapName = ""

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
            if playerAmountOnline > 0:
                for player in players:
                    playerList += player.name + ", "
                playerList = playerList[:-2]  # Remove last comma
                playerList += "."
        except:
            logger.error("Error getting local server status")
        

        try:
            tps = self.rcon.command("tps")
        except:
            logger.error("Rcon connection failed")
            self.rconConnect()
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
        while True:  # TODO: add stop flag
            localStatus = self.localServer.status()
            playerAmountOnline = localStatus.players.online
            if playerAmountOnline != self.previousPlayerAmountOnline:
                logger.debug("Playercount changed!")
                self.previousPlayerAmountOnline = playerAmountOnline
                if playerAmountOnline == 1:
                    await sendNotifications("Someone started playing on the server :D")
                elif playerAmountOnline == 0:
                    await sendNotifications("Awh, the server is all empty now :(")
            await asyncio.sleep(0.5)

    def say(self, message):
        self.command("say " + message)

    def command(self, message):
        try:
            self.rcon.command(message)
        except BrokenPipeError:
            logger.error("No Pipe for RCON command")
            self.rconConnect()