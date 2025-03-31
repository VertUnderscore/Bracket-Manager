from helper_functions import getUserInfo
import challonge_integration

class DiscordMatch:
    def __init__(self, match):
        self.allInfo = getUserInfo()
        self.match = match
        self.player1 = None
        self.player2 = None
        player1Found = False
        player2Found = False

        for participant in challonge_integration.getParticipants():
            if player1Found and player2Found:
                break
            
            #print(f"Current Participant: {participant}")
            if not player1Found and participant["id"] == self.match["player1_id"]:
                #print(f"We Found A Match For Player 1! {participant["name"]}")
                for user in self.allInfo:
                    if participant["name"].lower() == user["challonge_username"].lower():
                        self.player1 = user
                        break

                player1Found = True
                continue

            if not player2Found and participant["id"] == self.match["player2_id"]:
                #print(f"We Found A Match For Player 2! {participant["name"]}")
                for user in self.allInfo:
                    if participant["name"].lower() == user["challonge_username"].lower():
                        self.player2 = user
                        break
                
                player2Found = True
                continue
        
    def initialMessage(self):
        #Since there will be a lot of info, I will be doing this line by line and actually making this a function. I get this is slightly slower, but it makes the code more readable so I don't care. That's what python is for and this is a stupid discord bot anyways.
        round = challonge_integration.getRoundName(self.match["round"])
        returnString = ""
        returnString += f"Hello <@{self.player1["discord_id"]}> and <@{self.player2["discord_id"]}>\n"
        returnString += f"Welcome to the {challonge_integration.getRoundName(self.match["round"])}! Use this channel to schedule your matches!\n\n" if ((round.startswith("F")) or (round.startswith("S"))) else f"Welcome to {challonge_integration.getRoundName(self.match["round"])}! Use this channel to schedule your matches!\n\n"
        returnString += f"{self.player1["preferred_username"]}'s Info For Restreamers:\nTwitch: https://twitch.tv/{self.player1["twitch_username"]}"
        returnString += f", Pronouns: ({self.player1["pronouns"]})\n\n" if (self.player1["pronouns"] != "") else "\n\n" 
        returnString += f"{self.player2["preferred_username"]}'s Info For Restreamers:\nTwitch: https://twitch.tv/{self.player2["twitch_username"]}"
        returnString += f", Pronouns: ({self.player2["pronouns"]})\n\n" if (self.player2["pronouns"] != "") else "\n\n" 
        returnString += "Use this channel to schedule your match with your opponent! Once a time is selected between you two, then you can use /confirm_match to add it to the calendar! If you need to change the time for whatever reason, simply run the command again!\n"
        returnString += "Restreamers or commentators can use /claim to add that they will be restreaming or commentating the match, or /unclaim if they need to remove themself.\n"
        return returnString        
    
    def channel_name(self):
        return f"{self.player1["preferred_username"].lower()}-vs-{self.player2["preferred_username"].lower()}"
    
    def getDiscordIDs(self):
        returnArray = []
        returnArray.append(self.player1["discord_id"])
        returnArray.append(self.player2["discord_id"])
        return returnArray

if __name__ == "__main__":
    matches = challonge_integration.getCurrentMatches(1)
    for match in matches:
        y = DiscordMatch(match)
        print(f"Current Class Object: {y}")
        print(y.channel_name())
        print(y.initialMessage())


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