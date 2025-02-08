import discord # type: ignore #discord.py
import asyncio #async await functions
import challonge_integration
import match_to_discord
from user_info import getUserInfo
from config import bot_token # bot_token variable

all_users = getUserInfo()

class MyClient(discord.Client):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.guild = self.get_guild(1333486142430908537)        
        await self.discordRoundCreation(1)

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

    async def discordRoundCreation(self, round):
        category_name = f"Round {round}" #category name string
        category = discord.utils.get(self.get_all_channels(), name = category_name) # category type in discord.py
        for match in challonge_integration.getCurrentMatches(round):
            currentMatch = match_to_discord.DiscordMatch(match)
            channel_name = currentMatch.channel_name()
            if discord.utils.get(self.get_all_channels(), name = channel_name) != None:
                pass
            else:
                await self.guild.create_text_channel(channel_name, category=category)
                currentChannel = discord.utils.get(self.get_all_channels(), name = channel_name)
                for id in currentMatch.getDiscordIDs():
                    user = self.guild.get_member(id)
                    print(id)
                    print(user)
                    if user == None:
                        print("USER IS NONE FOR SOME REASON")
                    else:
                        await currentChannel.set_permissions(self.guild.get_member(id), view_channel=True)
                await currentChannel.send(currentMatch.initialMessage())


        print("Success")






def main():    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = MyClient(intents=intents)
    client.run(bot_token)


if __name__ == "__main__":
    main()