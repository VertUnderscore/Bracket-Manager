import challonge # type: ignore
import time
from config import CHALLONGE_API_KEY, CHALLONGE_USERNAME
challonge.set_credentials(CHALLONGE_USERNAME, CHALLONGE_API_KEY)
TOURNAMENT = "wijtbuaq" # Put Tournament Name

def getParticipants(): #makes code look nicer when calling outside of this file
    return challonge.tournaments.show(TOURNAMENT + "/participants") 

def getRoundName(round):
    if (round < 0):
        return f"Loser's Round {abs(round)}"
    elif (round == 3): #change number to the actual last round, this is the finals.
        return "Finals"
    elif (round == 2): #change to second last round. Semifinals
        return "Semifinals"
    else:
        return f"Round {round}"

def getTournamentNames():
    partipants = getParticipants()
    returnArray = []
    for partipant in partipants:
        returnArray.append(partipant["name"]) #get challonge names
    return returnArray

def getCurrentMatches():
    matches = challonge.tournaments.show(TOURNAMENT + "/matches")
    currentMatches = []
    for match in matches:
        if ((match["player1_id"] != None) and (match["player2_id"] != None)):
            currentMatches.append(match)
    
    return currentMatches

