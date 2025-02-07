import challonge # type: ignore
from config import challonge_api_key, challonge_username
challonge.set_credentials(challonge_username, challonge_api_key)
tournament = "wijtbuaq" # Put Tournament Name

def getParticipants(): #makes code look nicer when calling outside of this file
    return challonge.tournaments.show(tournament + "/participants") 

def getTournamentNames():
    partipants = getParticipants()
    returnArray = []
    for partipant in partipants:
        returnArray.append(partipant["name"]) #get challonge names
    return returnArray

def getCurrentMatches(round):
    matches = challonge.tournaments.show(tournament + "/matches")
    currentMatches = []
    for match in matches:
        if ((match["round"] == round) and (match["player1_id"] != None) and (match["player2_id"] != None)):
            currentMatches.append(match)
    
    return currentMatches