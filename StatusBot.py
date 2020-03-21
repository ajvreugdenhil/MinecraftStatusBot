import discord
from mcstatus import MinecraftServer
path_to_settings = "./bot.properties"

# Default settings
serverUrl = ""
localIp = '127.0.0.1'
queryPortString = 25565
rconPortString = 25575
rconPassword = ""
discordSecret = ""
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
    elif settingId == "DISCORD-SECRET":
        discordSecret = settingValue
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
if discordSecret == "":
    print("ERROR. No discord secret given")
if discordChannelName == "":
    print("ERROR. No discord channel given")

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
            playerList = ""
            mapName = ""

            try:
                urlStatus = urlServer.status()
                playerAmountOnline = urlStatus.players.online
                urlLatency = str(urlStatus.latency)
            except:
                print("Error while contacting server over url")

            try:
                localStatus = localServer.status()
                localLatency = str(localStatus.latency)
            except:
                print("Error while contacting server locally")

            try:
                query = localServer.query()
                playerList = ", ".join(query.players.names)
                mapName = query.map
            except:
                print("Error while executing query")
            

            response = "```"
            response += 'Status report: \n'
            response += "Domain is " + serverUrl + "\n"
            
            if urlLatency != -1:
                response += "The server replied over DNS in " + urlLatency + 'ms\n'
            else:
                response += "The server did not reply over DNS\n"

            if localLatency != -1:
                response += "The server replied over the local network in " + localLatency + " ms\n"
            else:
                response += "The server did not reply over the local network"

            if playerAmountOnline > 0:
                response += "The server has " + str(playerAmountOnline) + " players online.\n"
                response += "Online players: " + playerList + "\n"
            else:
                response += "No players are currently playing. Please do something about that :)\n"
            
            response += "Map: " + mapName + "\n"
        

            response += "```"
            await message.channel.send(response)



client = MyClient()
client.run(discordSecret)
