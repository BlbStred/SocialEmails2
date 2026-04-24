import os
import os.path
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from openai import OpenAI
from dotenv import load_dotenv # run 'pip install python-dotenv'
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        


def isRelevant(topic):
    return "new invitation" in topic
        

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



def getEmailList(category):
    service = get_gmail_service()
    
    # List messages (Gmail returns these in reverse chronological order by default)
    results = service.users().messages().list(userId='me', q=category).execute()
    messages = results.get('messages', [])

    result = []
    for msg in messages:
        # msg provides id only, fetch full message details
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        # Extract headers for display
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        # headers is a list of dictionaries {'name: ..., 'value': ...}
        # To get the subject, for example, find the first dictionary {'name: 'Subject', 'value': ...}
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender  = next((h['value'] for h in headers if h['name'] == 'From'),    'Unknown Sender')

        result.append(EmailMessage(msg['id'], sender, subject))

    return result



def sendEmail(emailList, isrelevant):
    # --- Configuration ---
    sender_email = "a.dan.brand@gmail.com"
    receiver_email = "a.dan.brand@gmail.com"
    password = "zxyf xhra flki fjsd"  # Use an App Password, not your login password
    
    subject = "Social Emails"
    body = "Received " + str(len(emailList)) + " social emails\n\n"
    for e in emailList:
        if (isRelevant(e.subject)):
            body += e.subject + "\n"
            




    

    # --- Creating the Message ---
    # We use 'utf-8' here to prevent the UnicodeEncodeError you encountered earlier
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        # --- Connecting to Server ---
        # For Gmail: smtp.gmail.com | Port: 587
        # For Outlook: smtp.office365.com | Port: 587
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        
        server.login(sender_email, password)
        
        # --- Sending ---
        server.send_message(msg)
        print("Email sent successfully!")

    except Exception as e:
        # Defensive error handling to keep the program running
        print(f"Error: {e}")
    
    finally:
        server.quit()




if __name__ == '__main__':
    emails = getEmailList('category:social')
    sendEmail(emails, isRelevant)
    for e in emails:
        print(e)

