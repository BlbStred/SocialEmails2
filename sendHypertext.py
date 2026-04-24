import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_link_email(target_msg_id):
    # --- Configuration ---
    sender_email = "your_email@gmail.com"
    receiver_email = "your_email@gmail.com"
    password = "your_app_password"
    
    # Construct the direct Gmail link
    gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{target_msg_id}"
    
    # --- Create the HTML Content ---
    # We use an <a> tag to create the hypertext link
    html_content = f"""
    <html>
      <body>
        <p>I have finished processing the email.<br><br>
           You can view the original message here: 
           <a href="{gmail_link}">View Original Email</a>
        </p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Processed: Direct Link to Message"

    # Attach the HTML version
    # The 'utf-8' encoding ensures your previous Unicode errors don't return
    part = MIMEText(html_content, "html", "utf-8")
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print(f"Link email sent for message {target_msg_id}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage:
# This ID would normally come from your message processing loop
current_msg_id = "18f123abc456def" 
send_link_email(current_msg_id)
