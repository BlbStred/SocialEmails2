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

# Get list of emails
