#!/usr/bin/python3.7

import RPi.GPIO as GPIO
import datetime
import logging
import os
import time
import requests

from pathlib import Path
from logging.handlers import TimedRotatingFileHandler


class BayWatch():
    def __init__(self):
        handler = TimedRotatingFileHandler('/var/log/BayWatch/main_log.txt', when="w6", interval=1, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter( formatter )

        self.logger = logging.getLogger("BayWatch Log")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

        self.logger.info('BayWatch.py start. %s ' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        self.config_file = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt'))
        self.config_dict = {}

    # Config file functions
    def load_config(self):
        config_file = open(self.config_file, 'r')

        config_dict = {}

        for line in config_file:
            line_list = line.rstrip().split(';')
            config_dict.update({line_list[0]: line_list[1]})

        return config_dict

    # Other functions
    def button_change(self, channel):
        url = "http://" + bay_watch.config_dict['server_address'] + '/modules/TrailerBay/UpdateTrailerBayDoorStatus.php'

        door_status = "ERROR"
        message = "ERROR"
        trailer_bay = "ERROR"
        write_data = "ERROR <br />"

        if channel == int(self.config_dict['gpio1']):
            filename = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door1.html'))
            trailer_bay = self.config_dict['trailer_bay1']
        elif channel == int(self.config_dict['gpio2']):
            filename = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door2.html'))
            trailer_bay = self.config_dict['trailer_bay2']

        if GPIO.input(channel) == 1:
            # Do stuff when it is closed... which is this?
            door_status = "CLOSED"
        if GPIO.input(channel) == 0:
            # Do stuff when it is opened... which is this?
            door_status = "OPEN"
                
        params = {'access_token': self.config_dict['access_token'], 'door_status': door_status, 'trailer_bay': trailer_bay}

        if door_status != "ERROR":
            try:
                r = requests.post(url = url, data = params)
                data = r.json()

                self.logger.info(url + ' ' + str(params) + ' ' + str(data))

                if data['success'] == True:
                    message = data['message']
                if data['success'] == False:
                    message = data['error']
            except Exception as e:
                self.logger.exception('Endpoint failed: %s: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))

        if channel == int(self.config_dict['gpio1']):
            write_data = """
        Door 1 Trailer Bay: {0} <br />
        Door 1 Status: {1} <br />
        Door 1 Message: {2} <br />
            """.format(trailer_bay, door_status, message)
        elif channel == int(self.config_dict['gpio2']):
            write_data = """
        Door 2 Trailer Bay: {0} <br />
        Door 2 Status: {1} <br />
        Door 2 Message: {2} <br />
            """.format(trailer_bay, door_status, message)
        
        #write info to file for html scraping later
        with open(filename, 'w') as output_file:
            output_file.write(write_data)

        filenames = [Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/header.html')), Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door1.html')), Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door2.html')), Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/footer.html'))]
        with open('/var/www/html/BayWatch.html', 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())

if __name__ == "__main__":    
    bay_watch = BayWatch()
    if bay_watch.config_file.is_file():
        bay_watch.config_dict = bay_watch.load_config()
    else:
        exit('Config File missing')

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(bay_watch.config_dict['gpio1']), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(int(bay_watch.config_dict['gpio1']), GPIO.BOTH, callback=bay_watch.button_change, bouncetime=250)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(bay_watch.config_dict['gpio2']), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(int(bay_watch.config_dict['gpio2']), GPIO.BOTH, callback=bay_watch.button_change, bouncetime=250)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()