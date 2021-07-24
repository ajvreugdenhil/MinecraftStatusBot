import discord
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MyClient(discord.Client):
    def __init__(self, getStatus, say, mcCommand, prefix=None, channelname=None, modRole=None):
        self.getStatus = getStatus
        self.say = say
        self.prefix = prefix
        self.channelname = channelname
        discord.Client.__init__(self)
        self.subscribers = []
        self.modRole = modRole
        self.mcCommand = mcCommand

    async def notify(self, message):
        logger.debug("Sending notifs")
        logger.debug(self.subscribers)
        for sub in self.subscribers:
            await self.get_channel(sub).send(message)

    async def on_ready(self):
        logger.info('Logged on as {0}'.format(self.user))

    async def on_message(self, message):
        # Don't respond to bots
        if message.author.bot:
            return
        if self.channelname == None and self.prefix == None:
            logger.error(
                "Prefix and channel not set. Ignoring message to prevent spam!")
            return

        # TODO: read discord response messages from translation file
        # that also allows the operator to cut out some cringe

        # Ignore all messages in irrelevant channels
        if not (message.channel.name == self.channelname or self.channelname == ""):
            return
        command = message.content.lower().split(" ")[0]

        if (self.prefix != None) and (not command.startswith(self.prefix)):
            return
        if self.prefix != None:
            command = command.replace(self.prefix, "")

        if (command == 'help'):
            logger.debug("help command received")
            await message.channel.send('Hi! I\'m the mc status bot. Find me at https://github.com/ajvreugdenhil/MinecraftStatusBot')
            await message.channel.send("Available commands: ```\n-help \n-sub \n-unsub \n-status \n-say \n-#script#```")

        if (command == 'sub'):
            logger.debug("sub command received")
            channelId = message.channel.id
            if channelId not in self.subscribers:
                self.subscribers.append(channelId)
                await message.channel.send("Liked and subscribed! 😄 Unsubscribe with \"unsub\"")
            else:
                await message.channel.send("Already subscribed!")

        if (command == 'unsub'):
            logger.debug("unsub command received")
            if (message.channel.id in self.subscribers):
                self.subscribers.remove(message.channel.id)
                await message.channel.send("😔 goodbye...")
            else:
                await message.channel.send("Uh oh, you weren't subscribed")

        if (command == 'status'):
            logger.debug("Status command received")
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
            await message.channel.send("Sent!")

        if (command[0:8] == '#script#'):
            logger.debug("script command received")
            if self.modRole == None:
                await message.channel.send("No mod role defined. Functionality disabled")
            else:
                if self.modRole not in [str(role.id) for role in message.author.roles]:
                    await message.channel.send("Insufficient rights")
                else:
                    await message.channel.send("Parsing...")
                    lines = message.content.split("\n")[1:]
                    logger.debug(lines)
                    if len(lines) < 1:
                        await message.channel.send("No commands received. use one command per line.")
                    else:
                        for line in lines:
                            if line[0] != '#':
                                logger.info("Running command: " + line)
                                self.mcCommand(line)
                    await message.channel.send("Done!")