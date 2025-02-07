import discord # type: ignore #discord.py
import asyncio #async await functions
from user_info import getUserInfo
from config import bot_token # bot_token variable

all_users = getUserInfo()
print(len(all_users))

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


def main():    
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(bot_token)


if __name__ == "__main__":
    main()