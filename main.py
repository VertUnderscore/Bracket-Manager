import discord # type: ignore #discord.py
from discord.ext import commands
import asyncio #async await functions
import json
import challonge_integration
import match_to_discord
import pytz
import re
from user_info import getUserInfo
from config import BOT_TOKEN, GUILD_ID, OWNER_ID
from typing import Literal, Optional
from timezone_map import timezone_map
from datetime import datetime, timedelta
import threading
import time

current_matches = {} # This will be updated periodically
async def listenerForMatches():
    global current_matches
    global client
    while True:
        print("Running")
        t_current_matches = challonge_integration.getCurrentMatches()
        if (current_matches == t_current_matches):
            print("Match Is Same")
            pass # base case, no need to do things
        else:
            print("Match Is Different")
            # Get match IDs or unique keys from the dictionaries
            current_ids = {match['id'] for match in current_matches}
            new_matches = [match for match in t_current_matches if match['id'] not in current_ids]
            current_matches = t_current_matches
            for x in new_matches:
                await client.discordRoundCreation(x["round"])
        await asyncio.sleep(60) # Only Pings Once Every 5 Minutes

def getUserInfo():
    returnArray = []
    user_info = {}
    with open('users.json', 'r') as file:
        user_info = json.load(file)
    
    for x in user_info: 
        returnArray.append(user_info[x])

    return returnArray

ALL_USERS = getUserInfo() # all user info array

class TournamentBot(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__("$", intents=intents)
        self.guild = self.get_guild(GUILD_ID)  
        self.owner_id = OWNER_ID # sets class owner_id as global owner ID

    async def on_ready(self):        
        print(f'Logged on as {self.user}!')
        asyncio.create_task(listenerForMatches())


    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

    async def discordRoundCreation(self, round):
        self.guild = self.get_guild(GUILD_ID)  #DRY except I have to because spaghetti code :(
        CATEGORY_NAME = challonge_integration.getRoundName(round)
        category = discord.utils.get(self.get_all_channels(), name = CATEGORY_NAME) # category type in discord.py
        if category == None:
            category = await self.guild.create_category_channel(CATEGORY_NAME)

        print(category)
        for match in current_matches:
            if match["round"] != round:
                continue
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
                        await currentChannel.set_permissions(user, view_channel=True)
                await currentChannel.send(currentMatch.initialMessage())

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = TournamentBot(intents=intents)

#Helper Function for confirm_match and update_match
def get_players_from_channel(channel_name):
        try:
            tplayer1, tplayer2 = channel_name.split("-vs-", 1)
            player1, player2 = None, None

            for user in ALL_USERS:
                if tplayer1 == user["preferred_username"].lower():
                    player1 = user
                elif tplayer2 == user["preferred_username"].lower():
                    player2 = user
                if player1 and player2:
                    break

            return player1, player2
        except ValueError:
            return None, None

# Helper Functions for confirm_match and update_match
### 🧩 **Helper Functions:**

def is_valid_channel(channel_name):
    """Check if channel name is valid (contains '-vs-')."""
    return "-vs-" in channel_name


def get_players_from_channel(channel_name):
    """Extract player names from the channel name."""
    try:
        tplayer1, tplayer2 = channel_name.split("-vs-", 1)
        player1, player2 = None, None

        for user in ALL_USERS:
            if tplayer1 == user["preferred_username"].lower():
                player1 = user
            elif tplayer2 == user["preferred_username"].lower():
                player2 = user
            if player1 and player2:
                break

        return player1, player2
    except ValueError:
        return None, None


def can_run_command(user, player1, player2):
    """Check if the user can run the command (either a player or a Tournament Admin)."""
    is_tourney_admin = any(role.name == "Tournament Admin" for role in user.roles)
    return (
        is_tourney_admin
        or user.id == player1["discord_id"]
        or user.id == player2["discord_id"]
    )


def generate_event_name(player1, player2):
    """Generate the event name."""
    return f"{player1['preferred_username']} ({player1['seed']}) vs {player2['preferred_username']} ({player2['seed']})"


def event_exists(scheduled_events, event_name):
    """Check if an event with the given name already exists."""
    return any(event.name == event_name for event in scheduled_events)


def parse_datetime(date_str, time_str):
    """Parse date and time string in both 12-hour and 24-hour formats."""
    time_formats = ["%I:%M %p", "%H:%M"]  # 12-hour and 24-hour formats

    for time_format in time_formats:
        try:
            return datetime.strptime(f"{date_str} {time_str}", f"%m/%d/%Y {time_format}")
        except ValueError:
            continue
    return None


def get_timezone(timezone):
    """Get the timezone object from abbreviation or UTC offset."""
    if timezone in timezone_map:
        return pytz.timezone(timezone_map[timezone])

    # Check for UTC offset pattern (e.g., UTC+5, UTC-3)
    utc_offset_match = re.match(r"UTC([+-]\d{1,2})(?::(\d{1,2}))?", timezone)

    if utc_offset_match:
        hours_offset = int(utc_offset_match.group(1))
        minutes_offset = int(utc_offset_match.group(2)) if utc_offset_match.group(2) else 0
        total_offset_minutes = hours_offset * 60 + minutes_offset
        return pytz.FixedOffset(total_offset_minutes)

    return None


async def create_event(guild, event_name, start_time, end_time, description="No restreamers or commentators have claimed this event"):
    """Create the scheduled event."""
    await guild.create_scheduled_event(
        name=event_name,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location="https://twitch.tv/supermarioworld",
        privacy_level=discord.PrivacyLevel.guild_only,
        entity_type=discord.EntityType.external,
    )
    

@client.tree.command(name="confirm_match", description="Use this command in your assigned match channel to confirm a match!")
@discord.app_commands.describe(date='Enter the date in MM/DD/YYYY Format', time="Enter the time in either 12 hour format or 24 hour format", timezone="Enter your local timezone.")
async def confirm_match(interaction: discord.Interaction, date: str, time: str, timezone: str):
    if not is_valid_channel(interaction.channel.name):
        await interaction.response.send_message(
            "Error: This command can only be used in private match scheduling channels.",
            ephemeral=True,
        )
        return

    player1, player2 = get_players_from_channel(interaction.channel.name)

    if not player1 or not player2:
        await interaction.response.send_message(
            "Error: Could not find player information. Check the channel name.",
            ephemeral=True,
        )
        return

    user_running_command = interaction.user

    # Check if user is authorized to run the command
    if not can_run_command(user_running_command, player1, player2):
        await interaction.response.send_message(
            "You do not have permission to run this command.", ephemeral=True
        )
        return

    # Generate event name and check if it already exists
    event_name = generate_event_name(player1, player2)

    if event_exists(interaction.guild.scheduled_events, event_name):
        await interaction.response.send_message(
            f"Error: An event with the name '{event_name}' already exists. Please use /update_match_time or ping a tournament admin.",
            ephemeral=True,
        )
        return

    # Parse and validate datetime
    dt_obj = parse_datetime(date, time)

    if not dt_obj:
        await interaction.response.send_message(
            "Invalid date or time format. Use 'MM/DD/YYYY' and 'H:MM AM/PM' or 'HH:MM'.",
            ephemeral=True,
        )
        return

    # Get timezone and convert to UTC
    timezone_obj = get_timezone(timezone)

    if not timezone_obj:
        await interaction.response.send_message(
            f"Unknown or unsupported timezone abbreviation: {timezone}",
            ephemeral=True,
        )
        return

    localized_dt = timezone_obj.localize(dt_obj)
    utc_dt = localized_dt.astimezone(pytz.UTC)
    end_dt = utc_dt + timedelta(hours=1)

    # Create event
    await create_event(interaction.guild, event_name, utc_dt, end_dt)
    await interaction.response.send_message(
        "Success! I have created an event for you!", ephemeral=True
    )

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
    client.run(BOT_TOKEN)

if __name__ == "__main__":
    main()