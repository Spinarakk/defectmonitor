# Import external libraries
import os
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyQt4.QtCore import QThread, SIGNAL


class Stopwatch(QThread):
    """ Module used to simulate a stopwatch"""

    def __init__(self):

        # Defines the class as a thread
        QThread.__init__(self)

        # Resets the stopwatch
        self.stopwatch_elapsed = 0
        self.stopwatch_idle = 0

        # Flag to start and terminate the while loop
        self.run_flag = True

    def run(self):
        while self.run_flag:
            # Send a formatted time string to the main function
            time_elapsed = self.convert2time(self.stopwatch_elapsed)
            time_idle = self.convert2time(self.stopwatch_idle)
            self.emit(SIGNAL("update_time(QString, QString)"), time_elapsed, time_idle)

            # Sleep for one second
            time.sleep(1)

            # Increment the stopwatch timers
            self.stopwatch_elapsed += 1
            self.stopwatch_idle += 1

            # Check if the countdown reaches 5 minutes, if so, send a signal back to the main program
            # if self.countdown == 300:
            #     self.emit(SIGNAL("send_notification()"))

    def convert2time(self, time):
        seconds = time % 60
        minutes = (time % 3600) / 60
        hours = time / 3600
        return '%s:%s:%s' % (str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2))

    def reset_time_idle(self):
        """Resets the countdown timer whenever this function is called"""

        self.stopwatch_idle = 0

    def stop(self):
        self.run_flag = False


class Notifications(QThread):
    """Module used to send email notifications to a specified email address"""

    def __init__(self, subject):

        # Defines the class as a thread
        QThread.__init__(self)

        # Load configuration settings from config.json file
        with open('config.json') as config:
            self.config = json.load(config)

        self.sender = 'donotreply.amaero@gmail.com'

        # Create the email here
        self.email = MIMEMultipart()
        self.email['From'] = self.sender
        self.email['To'] = self.config['EmailAddress']
        self.email['Subject'] = str(subject)
        self.email['X-Priority'] = '3'

        # Create the message here individually
        head = 'Dear %s,' % self.config['Username']
        body = 'This is a test email to see whether the email address is valid.'
        foot = ''

        # Create the full message by combining parts
        self.email.attach(MIMEText(head + '\n\n' + body + '\n\n' + foot, 'plain'))

    def run(self):
        self.send_notification()

    def send_notification(self):

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.sender, 'Amaero2017')
        server.sendmail(self.sender, self.config['EmailAddress'], self.email.as_string())
        server.quit()

    def add_attachment(self):
        pass


class FolderMonitor(QThread):
    """Module used to constantly poll the given folders and signal back if a change in number of items is detected"""

    def __init__(self, folders):

        # Defines the class as a thread
        QThread.__init__(self)

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
                length_new[index] = self.poll_folder(folder)

                # Emit a signal with the new length and the folder's index back to the MainWindow if different
                if not length_new[index] == length_old[index]:
                    # Length is incremented by one to prevent a maximum range of 0
                    self.emit(SIGNAL("folder_change(QString)"), str(index))
                    length_old[index] = length_new[index]

    def poll_folder(self, folder):
        """Checks the given folder and returns the number of files in that directory"""
        return len(os.walk(folder).next()[2])

    def stop(self):
        """Method that happens when the MainWindow is closed"""
        self.run_flag = False

