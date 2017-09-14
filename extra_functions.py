# Import external libraries
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyQt5.QtCore import *


class Notifications(QThread):
    """Module used to send email notifications including image attachments to a specified email address"""

    def __init__(self, subject, message, attachment_name=None):

        QThread.__init__(self)

        with open('config.json') as config:
            self.config = json.load(config)

        # Construct the email using the received subject and message
        self.message = MIMEMultipart()
        self.message['From'] = self.config['Notifications']['Sender']
        self.message['To'] = self.config['BuildInfo']['EmailAddress']
        self.message['Subject'] = subject
        self.message.attach(MIMEText(message, 'plain'))

        # Add the attachment if received
        if attachment_name:
            attachment = open(attachment_name, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= %s' % os.path.basename(attachment_name))
            self.message.attach(part)

    def run(self):
        # Connect to the gmail server, login to the default sender email and send the message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.config['Notifications']['Sender'], self.config['Notifications']['Password'])
        server.sendmail(self.config['Notifications']['Sender'], self.config['BuildInfo']['EmailAddress'],
                        self.message.as_string())
        server.quit()
