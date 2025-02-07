import json
def getUserInfo():
    returnArray = []
    user_info = {}
    with open('users.json', 'r') as file:
        user_info = json.load(file)
    
    for x in user_info: # this produces a string, but it's really weird. this code is going to get a list of users and their signup info. this will then store them all in an array.
        returnArray.append(user_info[x])

    return returnArray
