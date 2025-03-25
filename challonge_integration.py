import challonge # type: ignore
from config import CHALLONGE_API_KEY, CHALLONGE_USERNAME
challonge.set_credentials(CHALLONGE_USERNAME, CHALLONGE_API_KEY)
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