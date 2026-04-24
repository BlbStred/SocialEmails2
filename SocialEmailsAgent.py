import os
import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from openai import OpenAI
from dotenv import load_dotenv # run 'pip install python-dotenv'

# Load environmet variables from .env
load_dotenv()

# Reconfigure stdout to handle errors gracefully
sys.stdout.reconfigure(errors='replace')


class EmailMessage:
    def __init__(self, id, sender, subject):
        self.id      = str(id)
        self.sender  = str(sender)
        self.subject = str(subject)

    def __str__(self):
        result  =                self.id
        result += " from: "    + self.sender
        result += " subject: " + self.subject
        return result
        

        

def get_gmail_service():
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


# Get list of emails
def iterate_social_tab():
    service = get_gmail_service()
    
    # query for the Social category
    # 'category:social' is the Gmail search operator for the Social tab
    query = 'category:social'
    
    # List messages (Gmail returns these in reverse chronological order by default)
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    result = []
    for msg in messages:
        # Fetch full message details
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        # Extract headers for display
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

        result.append(EmailMessage(msg['id'], sender, subject))

    return result

        

if __name__ == '__main__':
    emails = iterate_social_tab()
    for e in emails:
        print(e)

