# Import external libraries
import os
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class Stopwatch(QThread):
    """Module used to simulate a stopwatch"""

    def __init__(self):

        QThread.__init__(self)

        # Reset the stopwatch
        self.stopwatch_elapsed = 0
        self.stopwatch_idle = 0

        # Flag to terminate the while loop
        self.run_flag = True

    def run(self):
        while self.run_flag:
            # Send a formatted time string to the main function
            time_elapsed = self.format_time(self.stopwatch_elapsed)
            time_idle = self.format_time(self.stopwatch_idle)
            self.emit(pyqtSignal("update_time(QString, QString)"), time_elapsed, time_idle)

            # Sleep for one second
            time.sleep(1)

            # Increment the stopwatch timers
            self.stopwatch_elapsed += 1
            self.stopwatch_idle += 1

            # Check if the countdown reaches 5 minutes, if so, send a signal back to the main program
            # if self.countdown == 300:
            #     self.emit(pyqtSignal("send_notification()"))

    def format_time(self, time):
        """Format the individual seconds, minutes and hours into a proper time format"""
        seconds = str(time % 60).zfill(2)
        minutes = str((time % 3600) / 60).zfill(2)
        hours = str(time / 3600).zfill(2)

        return '%s:%s:%s' % (hours, minutes, seconds)

    def reset_time_idle(self):
        """Resets the countdown timer whenever this function is called"""
        self.stopwatch_idle = 0

    def stop(self):
        """Stop the stopwatch entirely"""
        self.run_flag = False


class Notifications(QThread):
    """Module used to send email notifications to a specified email address
    Attachments such as images can be sent as well"""

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


class ExtraFunctions():


    def poll_folder(self, folders, callback):
        """Method used to poll the given folders and signal back if a change in number of items is detected"""




        # Store received argument as instance variable
        self.folders = folders

        # Flag to start and terminate the while loop
        self.run_flag = True

    def run(self):

        # Initialize a length of nothing to store the number of files in their respective folders
        length_old = [None, None, None, None, None]
        length_new = [None, None, None, None, None]

        while self.run_flag:
            # Loop through all five folders
            for index, folder in enumerate(self.folders):
                # Acquire the new length of the folder in question
                length_new[index] = len(os.walk(folder).next()[2])

                # Emit a signal with the new length and the folder's index back to the MainWindow if different
                if not length_new[index] == length_old[index]:
                    # Length is incremented by one to prevent a maximum range of 0
                    self.emit(pyqtSignal("folder_change(QString)"), str(index))
                    length_old[index] = length_new[index]

            # Delay the loop by a second to severely reduce CPU usage
            time.sleep(1)

    def stop(self):
        """Method that happens when the MainWindow is closed"""
        self.run_flag = False

