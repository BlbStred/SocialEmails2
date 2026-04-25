import os
import re
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
    def __init__(self, id, sender, subject, date):
        self.id      = str(id)
        self.sender  = str(sender)
        self.subject = str(subject)
        self.date    = str(date)        

    def __str__(self):
        result  =                self.id
        result += " from: "    + self.sender
        result += " subject: " + self.subject
        result += " date0: "   + self.date        
        return result



class EmailId:
    # Get the most recent id already processed previously
    idFileName = "latest_id.txt"

    def __init__(self):
        self.firstTime = True
    

    def processed(self, emailId):
        if self.firstTime:
            self.firstTime = False
            
            try:
                with open(EmailId.idFileName, "r") as file:
                    self.prevId = file.readline().split()[0]
            except:
                self.prevId     = ""        

            with open(EmailId.idFileName, "w") as file:
                file.write(emailId + " is the most recent email id already processed")
            

        return emailId == self.prevId

        
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
    # Get previously processed email id
    idService  = EmailId()
        
    service = get_gmail_service()
    
    # List messages (Gmail returns these in reverse chronological order by default)
    results = service.users().messages().list(userId='me', q=category).execute()
    messages = results.get('messages', [])

    result = []          # accumulates list of EmailMessages
    for msg in messages:
        # Check whether precessed previously
        msgId = msg['id']
        if idService.processed(msgId): break          # reached as far as last time
                
        # msg provides id only, fetch full message details
        message = service.users().messages().get(userId='me', id=msgId).execute()
        
        # Extract headers for display
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        # headers is a list of dictionaries {'name: ..., 'value': ...}
        # To get the subject, for example, find the first dictionary {'name: 'Subject', 'value': ...}
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender  = next((h['value'] for h in headers if h['name'] == 'From'),    'Unknown Sender')
        date    = next((h['value'] for h in headers if h['name'] == 'Date'),    'Unknown Date')
        date    = re.split(r'[+-]', date)[0]

        result.append(EmailMessage(msgId, sender, subject, date))

    return result



def sendEmail(emailList, isrelevant):

    relevant      = "<p>RELEVANT EMAILS:<br>"
    irrelevant    = "<p>IRRELEVANT EMAILS:<br>"    
    numRelevant   = 0
    numIrrelevant = 0
    
    for e in emailList:
        ref = f"""<a href=https://mail.google.com/mail/u/0/#inbox/{e.id}>
                {e.date}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{e.subject}
                </a><br>
        """
        
        if (isRelevant(e.subject)):
            relevant      += ref
            numRelevant   += 1
        else:
            irrelevant    += ref
            numIrrelevant += 1
            
    
    msg = MIMEMultipart("alternative")
    msg['From']    = "a.dan.brand@gmail.com"
    msg['To']      = "a.dan.brand@gmail.com"
    msg['Subject'] = "Social Emails"

    body = f"""
    <html>
      <body>
         Received {numRelevant} relevant and {numIrrelevant} irrelevant social emails.
         {relevant}
         {irrelevant}    
        </p>
      </body>
    </html>
    """
            
    msg.attach(MIMEText(body, 'html', 'utf-8'))


    try:
        # --- Connecting to Server ---
        # For Gmail: smtp.gmail.com | Port: 587
        # For Outlook: smtp.office365.com | Port: 587
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login("a.dan.brand@gmail.com",
                     "zxyf xhra flki fjsd")  # App Password, not login password
        server.send_message(msg)
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        server.quit()




if __name__ == '__main__':
    emails = getEmailList('category:social')
    sendEmail(emails, isRelevant)
    

