import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_brief_email():
    # --- Configuration ---
    sender_email = "a.dan.brand@gmail.com"
    receiver_email = "a.dan.brand@gmail.com"
    password = "zxyf xhra flki fjsd"  # Use an App Password, not your login password
    
    subject = "Quick Update"
    body = "Hello! This is a brief message sent from my Python script. \u034f"

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

if __name__ == "__main__":
    send_brief_email()
