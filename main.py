import discord # type: ignore #discord.py
from discord.ext import commands
import asyncio #async await functions
import challonge_integration
import match_to_discord
from user_info import getUserInfo
from config import bot_token, guild_id # bot_token variable
from typing import Literal, Optional
from timezone_map import timezone_map
from datetime import datetime, timedelta

all_users = getUserInfo()


class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__("$", intents=intents)
        self.guild = self.get_guild(guild_id)  
        self.owner_id = 180069278387535873

    async def on_ready(self):        
        print(f'Logged on as {self.user}!')

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
@discord.app_commands.describe(date='Enter the date in MM/DD/YYYY Format', time="Enter the time in either 12 hour format or 24 Hour Format", timezone="Enter your local timezone.")
async def schedule_match(interaction: discord.Interaction, date : str, time : str, timezone: str):
    # Try parsing time in both 12-hour and 24-hour formats
    time_formats = ["%I:%M %p", "%H:%M"]  # 12-hour and 24-hour formats
    dt_obj = None
    for time_format in time_formats:
        try:
            dt_obj = datetime.strptime(f"{date} {time}", f"%m/%d/%Y {time_format}")
            break
        except ValueError:
            continue

    if not dt_obj:
        await interaction.response.send_message("Invalid date or time format. Use 'MM/DD/YYYY' and 'H:MM AM/PM' or 'HH:MM'.", ephemeral=True)
        return

#Sync Command
@client.tree.command(name="sync", description="Sync Command")
async def sync(interaction: discord.Interaction):
    is_owner = await client.is_owner(interaction.user)
    if not is_owner:
        await interaction.response.send_message("You cannot run this command.", ephemeral=True)
        return

    print("Attempting to sync")
    try:
        synced = await client.tree.sync(guild=client.guild)
        print(f"Synced {len(synced)} commands to the guild")
        await interaction.response.send_message("Success!.", ephemeral=True)

    except Exception as e:
        print(f"Error: {e}")



def main():    
    client.run(bot_token)

if __name__ == "__main__":
    main()