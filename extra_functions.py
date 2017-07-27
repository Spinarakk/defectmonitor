# Import external libraries
import time
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

    def __init__(self):

        # Defines the class as a thread
        QThread.__init__(self)



        self.sender = 'donotreply.amaero@gmail.com'
        self.message = MIMEMultipart()
        self.message['From'] = self.sender
        self.message['To'] = 'nicholascklee@gmail.com'
        self.message['Subject'] = 'Image capture failed'
        self.message['X-Priority'] = '3'

        head = ''
        body = 'The program has failed to capture an image for the last 10 minutes. Please check status.'
        end = ''

        self.message.attach(MIMEText(head + body + end, 'plain'))

    def run(self):
        self.send_notification()

    def send_notification(self):

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.sender, 'Amaero2017')
        server.sendmail(self.sender, 'nicholascklee@gmail.com', self.message.as_string())
        server.quit()

    def add_attachment(self):
        pass