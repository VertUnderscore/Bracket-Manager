import discord # type: ignore #discord.py
from discord.ext import commands
import asyncio #async await functions
import challonge_integration
import match_to_discord
from user_info import getUserInfo
from config import bot_token # bot_token variable
from typing import Literal, Optional

all_users = getUserInfo()

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__("$", intents=intents)
        self.guild = self.get_guild(1333486142430908537)  

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

#I stole this because people in the discord.py server said to
@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    print("Command Ran")
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

def main():    
    client.run(bot_token)


if __name__ == "__main__":
    main()