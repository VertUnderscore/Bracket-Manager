import discord #discord.py
import asyncio #async await functions
import json
from config import bot_token # bot_token variable

user_info = {}

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
    print(user_info)
    print("Hello World!")



if __name__ == "__main__":
    main()