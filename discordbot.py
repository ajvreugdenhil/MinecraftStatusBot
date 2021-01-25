import discord
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MyClient(discord.Client):
    def __init__(self, getStatus, say):
        self.getStatus = getStatus
        self.say = say
        discord.Client.__init__(self)
        self.subscribers = []

    async def notify(self, message):
        logger.debug("Sending notifs")
        logger.debug(self.subscribers)
        for sub in self.subscribers:
            await self.get_channel(sub).send(message)

    async def on_ready(self):
        logger.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        discordChannelName = "famcrafttest"  # FIXME
        # Ignore all messages in irrelevant channels
        if not (message.channel.name == discordChannelName or discordChannelName == ""):
            return

        command = message.content.lower().split(" ")[0]

        '''
        # TODO: check for prefix
        if discordPrefix != "":
            command.replace(discordPrefix, "")
        '''

        if (command == 'help'):
            logger.debug("help command received")
            await message.channel.send("help, sub, unsub, status, say")

        if (command == 'sub'):
            logger.debug("sub command received")
            await message.channel.send("Liked and subscribed! 😄 Unsubscribe with \"unsub\"")
            channelId = message.channel.id
            if channelId not in self.subscribers:
                self.subscribers.append(channelId)

        if (command == 'unsub'):
            logger.debug("unsub command received")
            await message.channel.send("😔 goodbye...")
            self.subscribers.remove(message.channel.id)

        if (command == 'status'):
            logger.debug("Status command received")
            await message.channel.send('Hi! I\'m the mc status bot. Find me at github.com/ajvreugdenhil/MinecraftStatusBot')
            await message.channel.send(self.getStatus())

        if (command == 'say'):
            logger.debug("Send command received")
            if " " not in message.content:
                await message.channel.send("Send command requires 1 parameter")
                return
            messagebody = message.content.split(" ", 1)[1]
            sender = message.author.name
            payload = "<" + sender + "> " + messagebody
            self.say(payload)
