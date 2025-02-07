import challonge
from user_info import getUserInfo
from config import challonge_api_key, challonge_username
challonge.set_credentials(challonge_username, challonge_api_key)
tournament = "wijtbuaq" # Put Tournament Name
partipants = challonge.tournaments.show(tournament + "/participants")
matches = challonge.tournaments.show(tournament + "/matches")


def getTournamentNames():
    returnArray = []
    for x in partipants:
        returnArray.append(x["name"]) #get challonge names
    return returnArray

def getCurrentMatches(round):
    currentMatches = []
    for match in matches:
        if (match["round"] == round) and (match[]):
            
    

if __name__ == "__main__":
    user_info = getUserInfo()
    tournament_participants = getTournamentNames()
    
    for partipant in partipants:
        print(partipant["id"])