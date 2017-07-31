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
        self.stopwatch = 0
        self.countdown = 0
        self.seconds = 0
        self.minutes = 0
        self.hours = 0

        # Flag to start and terminate the while loop
        self.run_flag = True

    def run(self):
        while self.run_flag:
            # Send a formatted time string to the main function
            self.time = '%s:%s:%s' % (str(self.hours).zfill(2), str(self.minutes).zfill(2), str(self.seconds).zfill(2))
            self.emit(SIGNAL("update_stopwatch(QString)"), str(self.time))
            time.sleep(1)

            # Convert the counter into hours seconds and minutes
            self.stopwatch += 1
            self.seconds = self.stopwatch % 60
            self.minutes = int((self.stopwatch % 3600) / 60)
            self.hours = int(self.stopwatch / 3600)

            # Increment the countdown timer
            self.countdown += 1

            # Check if the countdown reaches 5 minutes, if so, send a signal back to the main program
            if self.countdown == 300:
                self.emit(SIGNAL("send_notification()"))

    def reset_countdown(self):
        """Resets the countdown timer whenever this function is called"""

        self.countdown = 0

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

    def __init__(self, folder_coat, folder_scan, folder_slice, frequency=1):

        # Defines the class as a thread
        QThread.__init__(self)

        self.folder_coat = folder_coat
        self.folder_scan = folder_scan
        self.folder_slice = folder_slice

        # How often (in seconds) to poll the folder
        self.frequency = frequency

        # Flag to start and terminate the while loop
        self.run_flag = True

    def run(self):

        # Initialize a length of nothing to store the number of files in their respective folders
        coat_length = None
        scan_length = None
        slice_length = None

        while self.run_flag:

            coat_length_new = self.poll_folder(self.folder_coat)
            scan_length_new = self.poll_folder(self.folder_scan)
            slice_length_new = self.poll_folder(self.folder_slice)

            # 1 is added to the length as an empty folder will cause the sliders to be set at 0, causing the new
            # minimum to be set as 0 as well
            # 0 -> Coat, 1 -> Scan, 2 -> Slice
            # Return current length of coat folder if changed
            if not coat_length_new == coat_length:
                self.emit(SIGNAL("update_layer_range(QString, QString)"), str(coat_length_new + 1), '0')
                coat_length = coat_length_new

            # Return current length of scan folder if changed
            if not scan_length_new == scan_length:
                self.emit(SIGNAL("update_layer_range(QString, QString)"), str(scan_length_new + 1), '1')
                scan_length = scan_length_new

            # Return current length of slice folder if changed
            if not slice_length_new == slice_length:
                self.emit(SIGNAL("update_layer_range(QString, QString)"), str(slice_length_new + 1), '2')
                slice_length = slice_length_new

            time.sleep(self.frequency)

    def poll_folder(self, folder):
        """Checks the given folder and returns the number of files in that directory"""
        return len(os.walk(folder).next()[2])

    def stop(self):
        """Method that happens when the MainWindow is closed"""
        self.run_flag = False

