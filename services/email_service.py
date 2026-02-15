import os
import resend
from flask import current_app


def send_email(to_email, subject, html_content, attachments=None):
   """
   Sends an email using Resend API.
   """
   try:
       import logging
       logger = logging.getLogger(__name__)
      
       api_key = os.environ.get("RESEND_API_KEY")
       if not api_key:
           logger.error("RESEND_API_KEY not found in environment variables.")
           return False
          
       resend.api_key = api_key


       sender = os.environ.get("EMAIL_SENDER", "Deliveroo <onboarding@resend.dev>")


       params = {
           "from": sender,
           "to": [to_email],
           "subject": subject,
           "html": html_content,
       }
      
       if attachments:
           params["attachments"] = attachments


       email = resend.Emails.send(params)
       logger.info(f"Email sent successfully: {email}")
       return True
   except Exception as e:
       logger.error(f"Failed to send email: {e}")
       return False