import discord
from mcstatus import MinecraftServer
path_to_settings = "./bot.properties"

# Default settings
serverUrl = ""
localIp = '127.0.0.1'
queryPortString = 25565
rconPortString = 25575
rconPassword = ""
discordToken = ""
discordChannelName = ""

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
    else:
        print("ERROR, invalid settingId! " + settingId + ":" + settingValue)

# Convert ports to integers
queryPort = int(queryPortString)
rconPort = int(rconPortString)

# Check obligatory settings
if serverUrl == "":
    print("ERROR. No serverurl given")
if discordToken == "":
    print("ERROR. No discord bot token given")
if discordChannelName == "":
    print("ERROR. No discord channel given")

#print(localIp + ':' + str(queryPort))
localServer = MinecraftServer(localIp, queryPort)
urlServer = MinecraftServer(serverUrl, queryPort)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content == 'status' and message.channel.name == discordChannelName:
            await message.channel.send('Hey Hey I\'m the New Famcraft bot')

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
                    playerList += player.name + "\n"
            except:
                print("Error while contacting server locally")
            
            response = "```"
            response += 'Status report for' + serverUrl + ': \n'
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
            else:
                response += "The server did not reply over the local network\n"
            response += "```"
            await message.channel.send(response)

client = MyClient()
client.run(discordToken)
