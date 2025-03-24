import discord # type: ignore #discord.py
from discord.ext import commands
import asyncio #async await functions
import challonge_integration
import match_to_discord
from user_info import getUserInfo
from config import bot_token, guild_id # bot_token variable
from typing import Literal, Optional
from timezone_map import timezone_map

all_users = getUserInfo()


class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents.all()):
        super().__init__("$", intents=intents)
        self.guild = self.get_guild(guild_id)  

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        try:
            synced = await self.tree.sync(guild=self.guild)
            print(f"Synced {len(synced)} commands to the guild")
        except Exception as e:
            print(f"Error: {e}")

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = MyClient(intents=intents)

@client.tree.command(name="hello", description="Says Hello World")
async def hello(interaction: discord.Interaction):
   # print(arg1)
    await interaction.response.send_message("Hello, world!")

@client.tree.command(name="schedule_match", description="Use this command in your assigned match channel to schedule a match!")
async def schedule_match(interaction: discord.Interaction, date : str, time : str, timezone: str):
    await interaction.response.send_message("Test")

def main():    
    client.run(bot_token)


if __name__ == "__main__":
    main()