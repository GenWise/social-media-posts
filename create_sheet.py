#!/usr/bin/env python3
"""
Create Google Sheet for Social Media Post Tracking.
Uses OAuth authentication (rajesh@genwise.in).
"""

import os
import pickle
from googleapiclient.discovery import build

# Configuration - OAuth token
TOKEN_PATH = os.path.expanduser("~/.config/gcp/google_oauth_token.pickle")

# Sheet structure
SHEET_TITLE = "Club GW Social Media Posts"
HEADERS = [
    "Thread Title",
    "Thread URL",
    "Status",
    "Platform",
    "Scheduled Date",
    "Posted Date",
    "Message",
    "Hashtags",
    "Media",
    "Engagement",
    "Notes"
]

# Club GW threads data
THREADS = [
    {"title": "How Harvard Makes $600M", "slug": "how-harvard-makes-600m", "hook": "Game theory of elite college money-making", "category": "Economics"},
    {"title": "The Pomato: When Science Gets Weird", "slug": "the-pomato-when-science-gets-weird", "hook": "Tomatoes + potatoes = botanical abomination", "category": "Science"},
    {"title": "Is Mathematics Discovery or Invention?", "slug": "is-mathematics-discovery-or-invention", "hook": "Philosophical debate with practical examples", "category": "Philosophy"},
    {"title": "What Exactly is Fire?", "slug": "what-exactly-is-fire", "hook": "Plasma, gas, or pure energy?", "category": "Chemistry"},
    {"title": "The Pam and Sam Logic Puzzle", "slug": "the-pam-and-sam-logic-puzzle", "hook": "A math puzzle that stumped ChatGPT", "category": "Mathematics"},
    {"title": "Battery Power vs Motor RPM", "slug": "battery-power-vs-motor-rpm", "hook": "RC plane builders debug physics", "category": "Engineering"},
    {"title": "Can You Lick Uranium?", "slug": "can-you-lick-uranium", "hook": "Which element kills you fastest?", "category": "Chemistry"},
    {"title": "How Do Ants Navigate?", "slug": "how-do-ants-navigate", "hook": "Pheromone trails and emergent algorithms", "category": "Biology"},
    {"title": "Why Do Birds Stand on One Leg?", "slug": "why-do-birds-stand-on-one-leg", "hook": "Thermoregulation meets anatomy", "category": "Biology"},
    {"title": "WRO Nationals Victory!", "slug": "wro-nationals-victory", "hook": "Club GW represents India in Singapore", "category": "Achievement"},
    {"title": "What is a Solid, Really?", "slug": "what-is-a-solid-really", "hook": "Can a powder flow like liquid?", "category": "Physics"},
    {"title": "Understanding Torque", "slug": "understanding-torque", "hook": "Why pushing a door at the edge feels easier", "category": "Physics"},
    {"title": "King George VI's Constitutional Paradox", "slug": "king-george-vi-s-constitutional-paradox", "hook": "The king at war with himself", "category": "History"},
]


def create_sheet():
    """Create and configure the Google Sheet."""
    # Authenticate with OAuth
    with open(TOKEN_PATH, 'rb') as token:
        credentials = pickle.load(token)

    sheets_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    # Create spreadsheet
    spreadsheet = {
        'properties': {'title': SHEET_TITLE},
        'sheets': [{
            'properties': {
                'title': 'Posts',
                'gridProperties': {'frozenRowCount': 1}
            }
        }]
    }

    result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = result['spreadsheetId']
    print(f"Created spreadsheet: {spreadsheet_id}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    # Add headers
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='Posts!A1',
        valueInputOption='RAW',
        body={'values': [HEADERS]}
    ).execute()

    # Add thread data as draft posts
    rows = []
    for thread in THREADS:
        url = f"https://clubgw.genwise.in/threads/{thread['slug']}/"
        rows.append([
            thread['title'],
            url,
            "Draft",  # Status
            "",  # Platform - to be decided
            "",  # Scheduled Date
            "",  # Posted Date
            "",  # Message - to be written
            f"#ClubGW #{thread['category']} #GenWise #CuriousMinds",
            "",  # Media
            "",  # Engagement
            thread['hook']  # Notes - using hook as starting point
        ])

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range='Posts!A2',
        valueInputOption='RAW',
        body={'values': rows}
    ).execute()

    # Format header row (bold, background color)
    requests = [
        {
            'repeatCell': {
                'range': {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.6},
                        'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        },
        # Auto-resize columns
        {
            'autoResizeDimensions': {
                'dimensions': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': len(HEADERS)}
            }
        },
        # Add data validation for Status column
        {
            'setDataValidation': {
                'range': {'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 100, 'startColumnIndex': 2, 'endColumnIndex': 3},
                'rule': {
                    'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': 'Draft'}, {'userEnteredValue': 'Scheduled'}, {'userEnteredValue': 'Posted'}, {'userEnteredValue': 'Skip'}]},
                    'showCustomUi': True
                }
            }
        },
        # Add data validation for Platform column
        {
            'setDataValidation': {
                'range': {'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 100, 'startColumnIndex': 3, 'endColumnIndex': 4},
                'rule': {
                    'condition': {'type': 'ONE_OF_LIST', 'values': [
                        {'userEnteredValue': 'Instagram'},
                        {'userEnteredValue': 'LinkedIn'},
                        {'userEnteredValue': 'Twitter'},
                        {'userEnteredValue': 'WhatsApp'},
                        {'userEnteredValue': 'Facebook'},
                        {'userEnteredValue': 'All'}
                    ]},
                    'showCustomUi': True
                }
            }
        }
    ]

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    # Already owned by rajesh@genwise.in via OAuth
    return spreadsheet_id


if __name__ == "__main__":
    sheet_id = create_sheet()
    print(f"\nSheet created successfully!")
    print(f"Open: https://docs.google.com/spreadsheets/d/{sheet_id}")
