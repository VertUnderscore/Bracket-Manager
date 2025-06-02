import json
from datetime import datetime
from timezone_map import timezone_map
import pytz
import discord
import re

def getUserInfo():
    returnArray = []
    user_info = {}
    with open('users.json', 'r') as file:
        user_info = json.load(file)
    
    for x in user_info: 
        returnArray.append(user_info[x])

    return returnArray
ALL_USERS = getUserInfo() # all user info array


#Helper Function for confirm_match
        
def get_preferred_name(id):
    try:
        for user in ALL_USERS:
            if id == user["discord_id"]:
                return user["preferred_username"]
    except ValueError:
        return None

# Helper Functions for confirm_match
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

def can_run_command_RC(user):
    is_commentator = any(role.name == "commentator" for role in user.roles)
    is_restreamer = any(role.name == "restreamer" for role in user.roles)
    is_tourney_admin = any(role.name == "Tournament Admin" for role in user.roles)
    return {is_commentator or is_restreamer or is_tourney_admin}

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

def parse_event_status(event_description):
    no_claim_pattern = r"No restreamers or commentators have claimed this event"
    claim_pattern = (
        r"Restreamers:\s*(?P<restreamer>[\w\s,]+)\s*"
        r"Commentators:\s*(?P<commentator>[\w\s,]+)"
    )

    # Check for no claims
    if re.search(no_claim_pattern, event_description):
        return {"restreamer": [], "commentator": []}

    # Check for claimed restreamers/commentators
    claim_match = re.search(claim_pattern, event_description)
    if claim_match:
        restreamers = [name.strip() for name in claim_match.group("restreamer").split(",") if name.strip() and name.strip().lower() != "none"]
        commentators = [name.strip() for name in claim_match.group("commentator").split(",") if name.strip() and name.strip().lower() != "none"]
        return {"restreamer": restreamers, "commentator": commentators}

    # Return None if neither pattern matches
    return None


async def update_event(guild, event_name, start_time, end_time, description="No restreamers or commentators have claimed this event"):
    #Update the scheduled event
    allEvents = await guild.fetch_scheduled_events()
    currentEvent = discord.utils.get(allEvents, name=event_name)

    await currentEvent.edit(
        name=event_name,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location="https://twitch.tv/supermarioworld",
        privacy_level=discord.PrivacyLevel.guild_only,
        entity_type=discord.EntityType.external,
    )

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

for user in ALL_USERS:
    print(user["preferred_username"])