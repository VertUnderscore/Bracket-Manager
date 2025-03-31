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