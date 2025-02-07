import user_info
import challonge_integration

class DiscordMatch:
    def __init__(self, match):
        self.allInfo = user_info.getUserInfo()
        self.match = match
        self.player1 = None
        self.player2 = None
        player1Found = False
        player2Found = False

        for participant in challonge_integration.getParticipants():
            if player1Found and player2Found:
                break
            
            print(f"Current Participant: {participant}")
            if not player1Found and participant["id"] == self.match["player1_id"]:
                print(f"We Found A Match For Player 1! {participant["name"]}")
                print(participant)
                for user in self.allInfo:
                    if participant["name"].lower() == user["challonge_username"].lower():
                        self.player1 = user
                        print('LOOK AT THIS LINE!!!')
                        print(self.player1)
                        break

                player1Found = True
                continue

            if not player2Found and participant["id"] == self.match["player2_id"]:
                print(f"We Found A Match For Player 2! {participant["name"]}")
                for user in self.allInfo:
                    if participant["name"].lower() == user["challonge_username"].lower():
                        self.player2 = user
                        break
                
                player2Found = True
                continue
        
    def initialMessage(self):
        return f"Hello <@{self.player1["discord_id"]}> and <@{self.player2["discord_id"]}> \nWelcome to Round {self.match["round"]}! Use this channel to schedule your matches!\n "
        
    def channel_name(self):
        return f"{self.player1["preferred_username"].lower()}-vs-{self.player2["preferred_username"].lower()}"

if __name__ == "__main__":
    matches = challonge_integration.getCurrentMatches(1)
    for match in matches:
        y = DiscordMatch(match)
        print(f"Current Class Object: {y}")
        print(y.channel_name())
        print(y.initialMessage())