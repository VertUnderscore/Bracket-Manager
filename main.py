import discord # type: ignore #discord.py
import discord.utils
from discord.ext import commands
import asyncio #async await functions
import json
import challonge_integration
import match_to_discord
import pytz
import re
from google_calendar_integration import GoogleCalendar
from config import BOT_TOKEN, GUILD_ID, OWNER_ID
from typing import Literal, Optional
from timezone_map import timezone_map
from datetime import datetime, timedelta
from helper_functions import *

current_matches = {} # This will be updated periodically
my_calendar = GoogleCalendar()

async def listenerForMatches():
    global current_matches
    global client
    while True:
        #print("Running")
        t_current_matches = challonge_integration.getCurrentMatches()
        if (current_matches == t_current_matches):
            #print("Match Is Same")
            pass # base case, no need to do things
        else:
            print("New Match ")
            # Get match IDs or unique keys from the dictionaries
            current_ids = {match['id'] for match in current_matches}
            new_matches = [match for match in t_current_matches if match['id'] not in current_ids]
            current_matches = t_current_matches
            for x in new_matches:
                await client.discordRoundCreation(x["round"])
        await asyncio.sleep(60) # Only Pings Once Every Minute


class BracketManager(commands.Bot):
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

        #print(category)
        for match in current_matches:
            if match["round"] != round:
                continue

            if not match.get("player1_id") or not match.get("player2_id"):
                print("Skipping match due to missing player data:", match)
                print(match)
                continue

            currentMatch = match_to_discord.DiscordMatch(match)
            channel_name = currentMatch.channel_name()
            if discord.utils.get(self.get_all_channels(), name = channel_name) != None:
                pass
            else:
                currentChannel = await self.guild.create_text_channel(channel_name, category=category)
                discord_ids = currentMatch.getDiscordIDs()
                print(f"Retrieved Discord IDs for channel {channel_name}: {discord_ids}")
                for id in discord_ids:
                    user = self.guild.get_member(id)
                    if user == None:
                        print(f"Failed to find user with ID {id} for channel {channel_name}")
                        # Try fetching the member directly
                        try:
                            user = await self.guild.fetch_member(id)
                            print(f"Successfully fetched user {user.name} after retry")
                        except discord.NotFound:
                            print(f"User with ID {id} not found in guild")
                        except discord.HTTPException as e:
                            print(f"HTTP error when fetching user {id}: {e}")
                    if user:
                        try:
                            await currentChannel.set_permissions(user, view_channel=True)
                            print(f"Successfully set permissions for user {user.name} in channel {channel_name}")
                        except discord.Forbidden as e:
                            print(f"Bot lacks permissions to set channel permissions: {e}")
                        except Exception as e:
                            print(f"Error setting permissions for user {user.name}: {e}")
                await currentChannel.send(currentMatch.initialMessage())

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = BracketManager(intents=intents)

@client.tree.command(name="unclaim", description="Use this command if you are a restreamer or commentator to remove yourself from the schedule")
async def unclaim(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        if not is_valid_channel(interaction.channel.name):
            await interaction.followup.send(
                "Error: This command can only be used in private match scheduling channels.",
                ephemeral=True,
            )
            return

        player1, player2 = get_players_from_channel(interaction.channel.name)

        if not player1 or not player2:
            await interaction.followup.send(
                "Error: Could not find player information. Check the channel name.",
                ephemeral=True,
            )
            return

        user_running_command = interaction.user

        # Check if user is authorized to run the command REWRITE THIS
        # As of 6/6 this command now works.
        if not can_run_command(user_running_command, player1, player2):
            await interaction.followup.send(
                "You do not have permission to run this command.", ephemeral=True
            )
            return

        event_name = generate_event_name(player1, player2)
        allEvents = await interaction.guild.fetch_scheduled_events()
        currentEvent = discord.utils.get(allEvents, name=event_name)
        event_description = currentEvent.description
        user_id = interaction.user.id
        username = None
        if (get_preferred_name(user_id)) == None:
            username = interaction.user.display_name
        else:
            username = get_preferred_name(user_id)

        if currentEvent is None:
            await interaction.followup.send("No event has been made.", ephemeral=True)
            return

        data = parse_event_status(event_description)
        
        if data is None:
            raise ValueError("Invalid event description format")

        #Remove from role_key
        role_key = ["restreamer", "commentator"]
        removed = False
        for role in role_key:
            data[role] = [entry for entry in data[role] if entry["name"] != username]
            if len(data[role]) < len(data[role]):
                removed = True

        # Rebuild the event description
        if not data["restreamer"] and not data["commentator"]:
            returnString = "No restreamers or commentators have claimed this event"
            await currentEvent.edit(description=returnString)
            await my_calendar.updateEventDescription(event_name, returnString)
            await interaction.followup.send("I have removed you from the schedule.", ephemeral=True)
            return
        
        def format_names_with_community(entries):
            if not entries:
                return "None"
            return ", ".join(f"{entry['name']} [{entry['community']}]" for entry in entries)
        
        restreamers_str = format_names_with_community(data["restreamer"])
        commentators_str = format_names_with_community(data["commentator"])
        
        new_description = f"Restreamers: {restreamers_str}\nCommentators: {commentators_str}"
        await currentEvent.edit(description=new_description)
        await my_calendar.updateEventDescription(event_name, new_description)
        await interaction.followup.send("I have removed you from the schedule.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send("You broke the bot somehow. I don't know how but you did. Please message Vert whatever you did, so that she can fix it!")
        print(e)

@client.tree.command(name="claim", description="Use this command if you're a restreamer or commentator to add yourself to the schedule")
@discord.app_commands.describe(
    role="Enter either 'restreamer' or 'commentator'",
    community="Enter your community (EN, JP, or BR)"
)
async def claim(interaction: discord.Interaction, role: str, community: str):
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        # Validate community
        community = community.upper()
        if community not in ["EN", "JP", "BR"]:
            await interaction.followup.send(
                "Error: Community must be either 'EN', 'JP', or 'BR'.",
                ephemeral=True,
            )
            return

        if not can_run_command_RC(interaction.user):
            await interaction.followup.send(
                "Error: You do not have permission to run this command.",
                ephemeral=True,
            )

        if not is_valid_channel(interaction.channel.name):
            await interaction.followup.send(
                "Error: This command can only be used in private match scheduling channels.",
                ephemeral=True,
            )
            return

        player1, player2 = get_players_from_channel(interaction.channel.name)

        if not player1 or not player2:
            await interaction.followup.send(
                "Error: Could not find player information. Check the channel name.",
                ephemeral=True,
            )
            return

        user_running_command = interaction.user

        # Check if user is authorized to run the command REWRITE THIS
        if not can_run_command(user_running_command, player1, player2):
            await interaction.followup.send(
                "You do not have permission to run this command.", ephemeral=True
            )
            return

        event_name = generate_event_name(player1, player2)
        allEvents = await interaction.guild.fetch_scheduled_events()
        currentEvent = discord.utils.get(allEvents, name=event_name)
        event_description = currentEvent.description
        user_id = interaction.user.id
        if get_preferred_name(user_id) == None:
            username = interaction.user.display_name
        else:
            username = get_preferred_name(user_id)

        if currentEvent is None:
            await interaction.followup.send("No event has been made.", ephemeral=True)
            return

        data = parse_event_status(event_description)
        
        if data is None:
            raise ValueError("Invalid event description format")

        role_key = role.lower()
        if role_key not in ["restreamer", "commentator"]:
            await interaction.followup.send("Role must be either 'restreamer' or 'commentator'", ephemeral=True)
            return

        # Add username with community if it's not already in the list
        user_entry = {"name": username, "community": community}
        if not any(entry["name"] == username for entry in data[role_key]):
            data[role_key].append(user_entry)

        # Rebuild the event description
        if not data["restreamer"] and not data["commentator"]:
            return "No restreamers or commentators have claimed this event"
        
        def format_names_with_community(entries):
            if not entries:
                return "None"
            return ", ".join(f"{entry['name']} [{entry['community']}]" for entry in entries)
        
        restreamers_str = format_names_with_community(data["restreamer"])
        commentators_str = format_names_with_community(data["commentator"])
        
        new_description = f"Restreamers: {restreamers_str}\nCommentators: {commentators_str}"
        await currentEvent.edit(description=new_description)
        await my_calendar.updateEventDescription(event_name, new_description)
        await interaction.followup.send("I have added you to the schedule.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send("You broke the bot somehow. I don't know how but you did. Please message Vert whatever you did, so that she can fix it!")
        print(e)


@client.tree.command(name="unconfirm_match", description="Use this command to remove a match from the schedule")
async def unconfirm_match(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not is_valid_channel(interaction.channel.name):
            await interaction.followup.send(
                "Error: This command can only be used in private match scheduling channels.",
                ephemeral=True,
            )
            return

        player1, player2 = get_players_from_channel(interaction.channel.name)
        
        if not player1 or not player2:
            await interaction.followup.send(
                "Error: Could not find player information. Check the channel name.",
                ephemeral=True,
            )
            return

        user_running_command = interaction.user
        
        # Check if user is authorized to run the command
        if not can_run_command(user_running_command, player1, player2):
            await interaction.followup.send(
                "You do not have permission to run this command.", ephemeral=True
            )
            return

        event_name = generate_event_name(player1, player2)

        # Check both Discord and Google Calendar for existing events
        discord_events = await interaction.guild.fetch_scheduled_events()
        event_status = event_exists(discord_events, event_name, my_calendar)
        
        if not event_status:
            await interaction.followup.send(
                "Error: This event does not exist in either Discord or Google Calendar.",
                ephemeral=True,
            )
            return

        discord_event = discord.utils.get(discord_events, name=event_name)
        google_event = my_calendar.getEventByName(event_name)

        # If both exist, delete both
        if discord_event and google_event:
            await discord_event.delete()
            await my_calendar.deleteEvent(event_name)
        # If only one exists, delete the one that exists
        elif discord_event and not google_event:
            await discord_event.delete()
        elif not discord_event and google_event:
            await my_calendar.deleteEvent(event_name)

        await interaction.followup.send(
            "I have removed this match from the schedule.",
            ephemeral=True,
        )
    except Exception as e:
        print(f"Error in unconfirm_match: {e}")
        await interaction.followup.send(
            "An error occurred while trying to remove the match from the schedule. Please try again or contact an administrator.",
            ephemeral=True,
        )


@client.tree.command(name="confirm_match", description="Use this command in your designated match channel to add or update a match in the schedule!")
@discord.app_commands.describe(date='Enter the date in MM/DD/YYYY Format', time="Enter the time in either 12 hour format or 24 hour format", timezone="Enter your local timezone.")
async def confirm_match(interaction: discord.Interaction, date: str, time: str, timezone: str):
    try: 
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        if not is_valid_channel(interaction.channel.name):
            await interaction.followup.send(
                "Error: This command can only be used in private match scheduling channels.",
                ephemeral=True,
            )
            return

        player1, player2 = get_players_from_channel(interaction.channel.name)

        if not player1 or not player2:
            await interaction.followup.send(
                "Error: Could not find player information. Check the channel name.",
                ephemeral=True,
            )
            return

        user_running_command = interaction.user

        # Check if user is authorized to run the command
        if not can_run_command(user_running_command, player1, player2):
            await interaction.followup.send(
                "You do not have permission to run this command.", ephemeral=True
            )
            return

        event_name = generate_event_name(player1, player2)

        # Parse and validate datetime
        dt_obj = parse_datetime(date, time)

        if not dt_obj:
            await interaction.followup.send(
                "Invalid date or time format. Use 'MM/DD/YYYY' and 'H:MM AM/PM' or 'HH:MM'.",
                ephemeral=True,
            )
            return

        # Get timezone and convert to UTC
        timezone_obj = get_timezone(timezone)

        if not timezone_obj:
            await interaction.followup.send(
                f"Unknown or unsupported timezone abbreviation: {timezone}",
                ephemeral=True,
            )
            return

        localized_dt = timezone_obj.localize(dt_obj)
        utc_dt = localized_dt.astimezone(pytz.UTC)
        end_dt = utc_dt + timedelta(hours=1)
        current_dt = datetime.now(pytz.UTC) # Fuck you Matthew. jk ily

        #Checks IF YOU ARE CREATING FOR A TIME IN THE PAST
        if (utc_dt <= current_dt):
            await interaction.followup.send(
                "You cannot create a time in the past ",
                ephemeral=True
            )
            return

        # Check both Discord and Google Calendar for existing events
        discord_events = await interaction.guild.fetch_scheduled_events()
        event_status = event_exists(discord_events, event_name, my_calendar)
        discord_event = discord.utils.get(discord_events, name=event_name)
        google_event = my_calendar.getEventByName(event_name)

        # Handle various cases
        if discord_event and google_event:
            # Both exist - update both
            await update_event(interaction.guild, event_name, utc_dt, end_dt)
            await my_calendar.updateEventTime(event_name, utc_dt, end_dt)
            await interaction.followup.send(
                f"Success! I have updated the schedule for you!",
                ephemeral=True,
            )
        elif discord_event and not google_event:
            # Only Discord event exists - create Google Calendar event
            await update_event(interaction.guild, event_name, utc_dt, end_dt)
            await my_calendar.createEvent(player1, player2, utc_dt, end_dt)
            await interaction.followup.send(
                f"Success! I have updated the schedule and synced with Google Calendar!",
                ephemeral=True,
            )
        elif not discord_event and google_event:
            # Only Google Calendar event exists - create Discord event and update Google Calendar
            await create_event(interaction.guild, event_name, utc_dt, end_dt)
            await my_calendar.updateEventTime(event_name, utc_dt, end_dt)
            await interaction.followup.send(
                "Success! I have recreated the Discord event and updated Google Calendar!",
                ephemeral=True
            )
        else:
            # Neither exists - create both
            await create_event(interaction.guild, event_name, utc_dt, end_dt)
            await my_calendar.createEvent(player1, player2, utc_dt, end_dt)
            await interaction.followup.send(
                "Success! I have created an event for you!", ephemeral=True
            )
    except Exception as e:
        print(f"{interaction.user}: {interaction.message}")
        print(e)
        await interaction.followup.send(
            "You broke the bot somehow. I don't know how, but you did. Please message Vert with what you did, and don't break the bot again.", ephemeral=True
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
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands to the guild")
        await interaction.response.send_message("Success!.", ephemeral=True)

    except Exception as e:
        print(f"Error: {e}")


def main():    
    client.run(BOT_TOKEN)

if __name__ == "__main__":
    main()

"""
MIT License

Copyright (c) 2025 VertUnderscore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""