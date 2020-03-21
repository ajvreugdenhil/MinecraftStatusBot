import discord
from mcrcon import MCRcon
from mcstatus import MinecraftServer
import sys

path_to_settings = "bot.properties"
if (len(sys.argv) > 1):
    path_to_settings = sys.argv[1]
print("using properties file: " + path_to_settings)

# Default settings
serverUrl = ""
localIp = '127.0.0.1'
queryPortString = 25565
rconPortString = 25575
rconPassword = ""
discordToken = ""
discordChannelName = ""
discordPrefix = ""

# Read all settings and write to variables
rawSettings = open(path_to_settings, "r")
settings = rawSettings.read().splitlines()
for setting in settings:
    settingAsList = setting.split("=")
    settingId = settingAsList[0]
    settingValue = settingAsList[1]
    if settingId == "SERVER-URL":
        serverUrl = settingValue
    elif settingId == "LOCAL-IP":
        localIp = settingValue
    elif settingId == "QUERY-PORT":
        queryPortString = settingValue
    elif settingId == "RCON-PORT":
        rconPortString = settingValue
    elif settingId == "RCON-PASSWORD":
        rconPassword = settingValue
    elif settingId == "DISCORD-TOKEN":
        discordToken = settingValue
    elif settingId == "DISCORD-CHANNEL-NAME":
        discordChannelName = settingValue
    elif settingId == "DISCORD-PREFIX":
        discordPrefix = settingValue
    else:
        print("ERROR, invalid settingId! " + settingId + ":" + settingValue)
rawSettings.close()

# Convert ports to integers
queryPort = int(queryPortString)
rconPort = int(rconPortString)

# Check obligatory settings
if serverUrl == "":
    print("ERROR. No serverurl given")
if discordToken == "":
    print("ERROR. No discord bot token given")

# Classes to pull data from
rcon = MCRcon(localIp, rconPassword)
rcon.connect()
localServer = MinecraftServer(localIp, queryPort)
urlServer = MinecraftServer(serverUrl, queryPort)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        #if not ((message.content.lower() == 'status') and discordPrefix == ''):
        #    return
        if not (message.content.lower() == (discordPrefix + 'status')):
            return
        if not (message.channel.name == discordChannelName or discordChannelName == ""):
            return

        await message.channel.send('Hi! I\'m the mc status bot. Find me at github.com/ajvreugdenhil/MinecraftStatusBot')

        tps = ""
        urlLatency = -1
        localLatency = -1
        playerAmountOnline = -1
        maxPlayerAmount = -1
        playerList = ""
        mapName = ""

        try:
            urlStatus = urlServer.status()
            urlLatency = str(urlStatus.latency)
        except:
            print("Error while contacting server over url")

        try:
            localStatus = localServer.status()
            localLatency = str(localStatus.latency)
            playerAmountOnline = localStatus.players.online
            maxPlayerAmount = localStatus.players.max
            for player in localStatus.players.sample:
                playerList += player.name + ", "
            playerList = playerList[:-2] #remove last comma
            playerList += "."
        except:
            print("Error while contacting server locally")

        try:
            tps = rcon.command("tps")
        except:
            print("Rcon connection failed")
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
        await message.channel.send(response)

client = MyClient()
client.run(discordToken)
