import discord # type: ignore #discord.py
import asyncio #async await functions
import challonge_integration
import match_to_discord
from user_info import getUserInfo
from config import bot_token # bot_token variable

all_users = getUserInfo()
print(len(all_users))

class MyClient(discord.Client):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.guild = self.get_guild(1333486142430908537)        
        await self.createChannel(1)

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

    async def createChannel(self, round):
        category_string = f"Round {round}"
        category = discord.utils.get(self.get_all_channels(), name = category_string)
        for match in challonge_integration.getCurrentMatches(1):
            currentMatch = match_to_discord.DiscordMatch(match)
            await self.guild.create_text_channel(currentMatch.channel_name(), category=category)
            currentChannel = discord.utils.get(self.get_all_channels(), name = currentMatch.channel_name())
            await currentChannel.send(currentMatch.initialMessage())


        print("Success")






def main():    
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(bot_token)


if __name__ == "__main__":
    main()