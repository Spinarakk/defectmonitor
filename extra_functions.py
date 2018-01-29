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

        with open('config.json') as config:
            self.config = json.load(config)

        self.notification = MIMEMultipart()
        self.notification['From'] = self.config['Notifications']['Sender']

    def test_notification(self, username, address, attachment_name):
        """Construct the message and attachment to be sent when the Send Test Email button is clicked"""

        self.notification['To'] = address
        self.notification['Subject'] = 'Test Email Notification'

        # Construct the full message here
        message = 'This is a test email addressed to %s to check if the entered email address is valid.' % username

        if attachment_name:
            self.attach_attachment(attachment_name)

        self.send_notification(message, address)

    def idle_notification(self, build_name, phase, layer, address, attachment_name):
        """Construct the message and attachment to be sent when an Idle Timeout is triggered"""

        self.notification['To'] = address
        self.notification['Subject'] = 'Build %s Idle Error' % build_name

        phases = ['Coat', 'Scan']

        # Construct the full message here
        notification = 'Defect Monitor has failed to capture an image in the last %s minutes.\n\nThis could be the ' \
                       'result of a machine malfunction, a part error, a camera issue, the magnetic trigger not ' \
                       'working correctly or the build has finished and because the user hadn\'t added any slice ' \
                       'files, the final layer number is unknown.\n\nAttached is the latest captured image, which ' \
                       'appears to be %s Layer %s.' % (self.config['IdleTimeout'] // 60, phases[phase], int(layer))

        if attachment_name:
            self.attach_attachment(attachment_name)

        self.send_notification(notification, address)

    def camera_notification(self, address):
        """Construct the message to be sent when an error in the camera is detected"""

        self.notification['To'] = address
        self.notification['Subject'] = 'Camera Error'

        notification = 'An error with the camera has been detected.\nThe camera has possibly shut down and is unable ' \
                       'to be detected by the computer.\nTry disconnecting and reconnecting the yellow ethernet cable' \
                       'connected to the POE switch.'

        self.send_notification(notification, address)

    def finish_notification(self, build_name, address):
        """Construct the message to be sent when the captured image layer number has exceeded the slice layer number"""

        self.notification['To'] = address
        self.notification['Subject'] = 'Build Finished'

        notification = 'The build\'s most recent layer number has exceeded the max layer number as determined by the ' \
                       'build\s entered slice files. As such, it is assumed that the current build has finished.' \
                       '\nRegardless, the program will still continue to capture additional images should the ' \
                       'trigger continue to be triggered.'

        self.send_notification(notification, address)

    def attach_attachment(self, name):
        """Attach the attachment to the notification email"""
        attachment = open(name, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= %s' % os.path.basename(name))
        self.notification.attach(part)

    def send_notification(self, notification, address):
        """Send the email after attaching the corresponding message"""

        self.notification.attach(MIMEText(notification, 'plain'))

        # Connect to the gmail server, login to the default sender email and send the message
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.config['Notifications']['Sender'], self.config['Notifications']['Password'])
        server.sendmail(self.config['Notifications']['Sender'], address,
                        self.notification.as_string())
        server.quit()
