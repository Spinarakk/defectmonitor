# Import external libraries
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyQt5.QtCore import *


class Notifications:
    """Module used to send email notifications including image attachments to a specified email address"""

    def __init__(self):

        with open('build.json') as build:
            self.build = json.load(build)

        # Construct the email using the received subject and message
        self.message = MIMEMultipart()
        self.message['From'] = self.build['Notifications']['Sender']
        self.message['To'] = self.build['BuildInfo']['EmailAddress']

        # Grab the attachment name (if it exists) (for clearer code purposes)
        attachment_name = self.build['Notifications']['Attachment']

        # Add the attachment if valid
        if attachment_name:
            attachment = open(attachment_name, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= %s' % os.path.basename(attachment_name))
            self.message.attach(part)

    def minor_defect_message(self):
        """Construct the message to be sent when a minor defect(s) has been detected"""

        self.message['Subject'] = 'Minor Defect(s) Found'

        # Construct the full message here
        message = 'Minor defects have been found in this layer.'

        self.send(message)

    def major_defect_message(self):
        """Construct the message to be sent when a major defect(s) has been detected"""

        self.message['Subject'] = 'Major Defect(s) Found'

        # Construct the full message here
        message = 'Major defects have been found in this layer.'

        self.send(message)

    def test_message(self):
        """Construct the message to be sent when the Send Test Email button is clicked"""

        self.message['Subject'] = 'Test Email Notification'

        # Construct the full message here
        message = 'This is a test email to check if the entered email address is valid.'

        self.send(message)

    def send(self, message):
        """Send the email after attaching the corresponding message"""

        self.message.attach(MIMEText(message, 'plain'))

        # Connect to the gmail server, login to the default sender email and send the message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.build['Notifications']['Sender'], self.build['Notifications']['Password'])
        server.sendmail(self.build['Notifications']['Sender'], self.build['BuildInfo']['EmailAddress'],
                        self.message.as_string())
        server.quit()
