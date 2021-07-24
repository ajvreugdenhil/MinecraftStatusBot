# MinecraftStatusBot

Python Discord bot to manage a Minecraft Server.

## Environment variables

The bot gets its config from environment variables. These can be specified in a .env and sourced when starting, or they may be specified in a docker compose file (recommended).

`SERVER_URL` (mandatory) specifies the domain of the server that all users connect through. This is displayed in the status command and used to get the online/offline status and ping time in the status command.

`LOCAL_IP` (defaults to 127.0.0.1) specifies the ip of the server in the local network. If this IP responds, but the domain doesnt, the issue might be DNS.

`QUERY_PORT` (defaults to 25565)

`RCON_PORT` (defaults to 25575)

`RCON_PASSWORD` (mandatory)

`DISCORD_TOKEN` (mandatory)

`DISCORD_CHANNEL_NAME` or `DISCORD_PREFIX` has to be set in order to limit spam by the bot.

`DISCORD_MOD_ROLE` has to be set to enable scripting. Only discord users with this role can start scripts.

## Road map

- [x] Generate message when players online goes from 0 to 1
- [x] Dockerize
- [ ] User driven whitelisting
- [ ] Full rewrite to allow one instance to manage many servers
