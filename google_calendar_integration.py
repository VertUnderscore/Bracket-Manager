import datetime
import os.path
from config import CALENDAR_ID
from helper_functions import generate_event_name

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendar:
    def __init__(self):
        SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        try:
            self.service = build("calendar", "v3", credentials=self.creds)

            # Call the Calendar API
            now = datetime.datetime.now().isoformat() + 'Z' 
            print("Getting the upcoming 10 events")
            events_result = (
                self.service.events()
                .list(
                    calendarId=CALENDAR_ID,
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            self.events = events_result.get("items", [])

            if not self.events:
                print("No upcoming events found.")
                return

            # Prints the start and name of the next 10 events
            for event in self.events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])

        except HttpError as error:
            print(f"An error occurred: {error}")

    def getEventByName(self, event_name):
        events_result = (
                self.service.events()
                .list(
                    calendarId=CALENDAR_ID,
                    timeMin=datetime.datetime.now().isoformat() + 'Z',
                    maxResults=100,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
        currentEvent = None
        events = events_result.get("items", [])
        for event in events:
            if (event["summary"] == event_name):
                currentEvent = event
                break
        
        return currentEvent


    async def createEvent(self, player1, player2, startTime, endTime):
        print("Creating Event On Google Calendar")
        event = {
            'summary': f'{generate_event_name(player1, player2)}',
            'location': "https://twitch.tv/supermarioworld",
            'description': 'No restreamers or commentators have claimed this event',
            'start': {
                'dateTime': f'{str(startTime.isoformat())}',
                'timeZone': "UTC",
            },
            'end': {
                'dateTime': f'{str(endTime.isoformat())}',
                'timeZone': "UTC",
            },
            'reminders': {
                'useDefault': True,
            },
        }

        event = self.service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print("Event Created")

    async def updateEventTime(self, event_name, startTime, endTime):
        event = self.getEventByName(event_name)
        event["start"]["dateTime"] = str(startTime.isoformat())
        event["end"]["dateTime"] = str(endTime.isoformat())
        self.service.events().update(calendarId=CALENDAR_ID, eventId=event["id"], body=event).execute()
        print("Updated Event Time")


    async def updateEventDescription(self, event_name, new_description):
        event = self.getEventByName(event_name)
        event["description"] = new_description
        self.service.events().update(calendarId=CALENDAR_ID, eventId=event["id"], body=event).execute()
        print("Updated Event Description")

    async def deleteEvent(self, event_name):
        """Delete an event from Google Calendar by its name."""
        event = self.getEventByName(event_name)
        if event:
            self.service.events().delete(calendarId=CALENDAR_ID, eventId=event["id"]).execute()
            print(f"Deleted event: {event_name}")
        else:
            print(f"Event not found: {event_name}")

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