from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import sys


sg = SendGridAPIClient(settings.SENDGRID_API_KEY)


def send_mail(to_emails, subject, html_content, attachment=None):
  is_test = 'test' in sys.argv

  if is_test:
    return

  message = Mail(
      from_email=('info@kwrts.com', "Socialize Berlin"),
      to_emails=to_emails,
      subject=subject,
      html_content=html_content
  )

  if attachment:
    message.attachment = attachment

  sg.send(message)
