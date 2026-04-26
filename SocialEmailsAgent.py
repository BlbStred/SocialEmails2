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



#######################################
# SERVICES
#######################################
        
gmailService = get_gmail_service() # To access gmail
idService  = EmailId()             # To check if email id previously processed
aiService  = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def analyze_comment(input_text):
    print(f"--- Analyzing: {input_text[:50]}... ---")
    
    try:
        # 2. The Request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a classifier. Answer 'YES' if the text is a comment on something, and 'NO' if it is not. Provide a brief reason."},
                {"role": "user", "content": input_text}
            ]
        )
        
        result = response.choices[0].message.content
        
        # 3. Defensive Printing 
        # Using .encode().decode() handles any stray characters like \u034f
        clean_result = result.encode('ascii', 'replace').decode('ascii')
        print(f"Result: {clean_result}")

    except Exception as e:
        # This catches API errors, connection issues, or encoding bugs
        print(f"An error occurred, but we're skipping it: {e}")


    
def isRelevant(topic):
    
    try:
        # 2. The Request
        response = aiService.chat.completions.create(
            model="gpt-4o",
            seed=42,
            messages=[
                {"role": "system", "content": "You are a classifier. Answer 'YES' if the text mentions an invitation, and 'NO' if it does not. Provide a brief reason."},
                {"role": "user", "content": topic}
            ]
        )
        
        result = response.choices[0].message.content
        
        # 3. Defensive Printing 
        # Using .encode().decode() handles any stray characters like \u034f
        clean_result = result.encode('ascii', 'replace').decode('ascii')
        print(topic, f"Result: {clean_result}")

    except Exception as e:
        # This catches API errors, connection issues, or encoding bugs
        print(f"An error occurred, but we're skipping it: {e}")
        result = ''

    answer = result.split()[0]
    print(answer)
    return answer == 'YES'



def getEmailList(category):
    
    # List messages (Gmail returns these in reverse chronological order by default)
    results = gmailService.users().messages().list(userId='me', q=category).execute()
    messages = results.get('messages', [])

    result = []          # accumulates list of EmailMessages
    for msg in messages:
        # Check whether precessed previously
        msgId = msg['id']
        if idService.processed(msgId): break          # reached as far as last time
                
        # msg provides id only, fetch full message details
        message = gmailService.users().messages().get(userId='me', id=msgId).execute()
        
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
        ref = f"""<a href=https://mail.google.com/mail/u/0/#inbox/{e.id} target="_blank" rel="noopener noreferrer">
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
    msg['From']    = os.environ.get("MY_GMAIL_ADDRESS")
    msg['To']      = os.environ.get("MY_GMAIL_ADDRESS")
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
        server.login(os.environ.get("MY_GMAIL_ADDRESS"),
                     os.environ.get("MY_GMAIL_APP_PASSWORD"))  # App Password, not login password
        server.send_message(msg)
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        server.quit()




if __name__ == '__main__':
    emails = getEmailList('category:social')
    sendEmail(emails, isRelevant)
    

