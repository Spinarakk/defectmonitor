# Import external libraries
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class Notifications:
    """Module used to send notification emails which may include image attachments to a specified email address"""

    def send(self, receiver, category, attachment_name='', info=None):
        """Construct the notification email by setting sending and receiving members and the text message itself
        Attach any received attachments and finally send the email to the specified receiver address"""

        # Load the sender and password from the config.json file
        with open('config.json') as config:
            settings = json.load(config)['Notifications']

        # Create the notification email itself as a MIME object
        email = MIMEMultipart()

        # Set the sending and receiving addresses
        email['From'] = settings['Sender']
        email['To'] = receiver

        # Set the subject line and the message itself, with different messages for different notification categories
        if 'test' in category:
            email, message = self.set_test(email, info)
        elif 'idle' in category:
            email, message = self.set_idle(email, info[0], info[1], info[2], info[3])
        elif 'camera' in category:
            email, message = self.set_camera(email)
        elif 'finish' in category:
            email, message = self.set_finish(email, info)

        # Attach the message to the email
        email.attach(MIMEText(message, 'plain'))

        # Attach the attachment to the email if one was sent
        if attachment_name:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(open(attachment_name, 'rb').read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment; filename= %s' % os.path.basename(attachment_name))
            email.attach(attachment)

        # Finally, send the email to the receiving address by first connecting to the gmail server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to the set sender email address and finally send the message
        server.login(settings['Sender'], settings['Password'])
        server.sendmail(settings['Sender'], receiver, email.as_string())
        server.quit()

    @staticmethod
    def set_test(email, username):
        """Notification for when the Send Test Email button is clicked"""

        email['Subject'] = 'Test Email Notification'
        message = 'This is a test email addressed to %s to check if the entered email address is valid.' % username
        return email, message

    @staticmethod
    def set_idle(email, build_name, timeout, phase, layer):
        """Notification for when an Idle Timeout is triggered"""

        email['Subject'] = 'Build %s Idle Error' % build_name
        phases = ['Coat', 'Scan']
        message = 'Defect Monitor has failed to capture an image in the last %s minutes.\n\nThis could be the result ' \
                  'of a machine malfunction, a part error, a camera issue, the magnetic trigger not working correctly ' \
                  'or the build has finished and because the user hadn\'t added any slice files, the final layer ' \
                  'number is unknown.\n\nAttached is the latest captured image, which appears to be %s Layer %s.' % \
                  (timeout // 60, phases[phase], int(layer))
        return email, message

    @staticmethod
    def set_camera(email):
        """Notification for when an error in the camera is detected"""

        email['Subject'] = 'Camera Error'
        message = 'An error with the camera has been detected.\nThe camera has possibly shut down and is unable to be ' \
                  'detected by the computer.\nTry disconnecting and reconnecting the yellow ethernet cable connected ' \
                  'to the POE switch. '
        return email, message

    @staticmethod
    def set_finish(email, build_name):
        """Notification for when the captured image layer number has exceeded the maximum slice layer number"""

        email['Subject'] = 'Build %s Finished' % build_name
        message = 'The build\'s most recent layer number has exceeded the max layer number as determined by the ' \
                  'build\s entered slice files. As such, it is assumed that the current build has ' \
                  'finished.\nRegardless, the program will still continue to capture additional images should the ' \
                  'trigger continue to be triggered. '
        return email, message
