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

        self.notification = MIMEMultipart()
        self.notification['From'] = self.build['Notifications']['Sender']
        self.notification['To'] = self.build['BuildInfo']['EmailAddress']

    def test_message(self, attachment_name):
        """Construct the message and attachment to be sent when the Send Test Email button is clicked"""

        self.notification['Subject'] = 'Test Email Notification'

        # Construct the full message here
        message = 'This is a test email to check if the entered email address is valid.'

        if attachment_name:
            self.attach_attachment(attachment_name)

        self.send_notification(message)

    def idle_message(self, attachment_name, timeout):
        """Construct the message and attachment to be send when an Idle Timeout is triggered"""

        self.notification['Subject'] = 'Build %s Idle Error' % self.build['BuildInfo']['Name']

        phase = ['Coat', 'Scan']

        # Construct the full message here
        message = 'Defect Monitor has failed to capture an image in the last %s minutes.\nThis could be the result of ' \
                  'a machine malfunction, a part error, a camera issue, the magnetic trigger not working correctly or ' \
                  'the build has finished and because the user hadn\'t added any slice files, the final layer number ' \
                  'is unknown.\nAttached is the latest captured image, which appears to be %s Layer %s.' % \
                  (timeout, phase[self.build['ImageCapture']['Phase']], self.build['ImageCapture']['Layer'])

        if attachment_name:
            self.attach_attachment(attachment_name)

        self.send_notification(message)

    def attach_attachment(self, name):
        """Attach the attachment to the notification email"""
        attachment = open(name, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= %s' % os.path.basename(name))
        self.notification.attach(part)

    def send_notification(self, message):
        """Send the email after attaching the corresponding message"""

        self.notification.attach(MIMEText(message, 'plain'))

        # Connect to the gmail server, login to the default sender email and send the message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.build['Notifications']['Sender'], self.build['Notifications']['Password'])
        server.sendmail(self.build['Notifications']['Sender'], self.build['BuildInfo']['EmailAddress'],
                        self.notification.as_string())
        server.quit()
