#!/usr/bin/python3.7

import automationhat
import datetime
import logging
import os
import ST7735 as ST7735
import sys
import time
import requests

from fonts.ttf import RobotoBlackItalic as UserFont
from gpiozero import CPUTemperature
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

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
    def button_change(self, channel, door_status):
        url = "http://" + bay_watch.config_dict['server_address'] + '/modules/TrailerBay/UpdateTrailerBayDoorStatus.php'

        cpu = CPUTemperature()

        message = "ERROR"
        trailer_bay = "ERROR"
        write_data = "ERROR <br />"

        if channel == 0:
            filename = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door1.html'))
            trailer_bay = self.config_dict['trailer_bay1']

        elif channel == 2:
            filename = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door2.html'))
            trailer_bay = self.config_dict['trailer_bay2']
                
        params = {'access_token': self.config_dict['access_token'], 'door_status': door_status, 'trailer_bay': trailer_bay}

        #print(trailer_bay + ' ' + str(channel) + ' ' + door_status)

        try:
            r = requests.post(url = url, data = params)
            data = r.json()

            self.logger.info('url: ' + url + ' params: ' + str(params) + ' data: ' + str(data) + ' cpu temp: ' + str(cpu.temperature))

            if data['success'] == True:
                message = data['message']
            if data['success'] == False:
                message = data['error']

        except Exception as e:
            self.logger.exception('Endpoint failed: %s: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))

        if channel == 0:
            write_data = """
        {0}_door_status:{1} <br />
        {0}_door_message:{2} <br />
            """.format(trailer_bay, door_status, message)

        elif channel == 2:
            write_data = """
        {0}_door_status:{1} <br />
        {0}_door_message:{2} <br />
            """.format(trailer_bay, door_status, message)
        
        #write info to file for html scraping later
        with open(filename, 'w') as output_file:
            output_file.write(write_data)

        filenames = [Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/header.html')), Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door1.html')), Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/Door2.html')), Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HtmlFiles/footer.html'))]
        with open('/var/www/html/index.html', 'w') as outfile:
            outfile.write("cpu_temp:{temp:.2f}".format(temp=cpu.temperature))
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())

if __name__ == "__main__":
    #Initialize BayWatch specific variables
    bay_watch = BayWatch()
    if bay_watch.config_file.is_file():
        bay_watch.config_dict = bay_watch.load_config()
    else:
        exit('Config File missing')
        
    previous_one = True
    previous_two = True

    try:
        while True:
            #Perform input read baywatch_functions
            if automationhat.input[0].read() == 1:
                try:
                    if previous_one != True:
                        bay_watch.button_change(0, 'CLOSED')

                except Exception as e:
                    bay_watch.logger.exception('%s - Function call failed for input %s: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '1', e))

                previous_one = True
            elif automationhat.input[0].read() == 0:
                try:
                    if previous_one != False:
                        bay_watch.button_change(0, 'OPEN')

                except Exception as e:
                    bay_watch.logger.exception('%s - Function call failed for input %s: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '1', e))

                previous_one = False
            else:
                bay_watch.logger.exception('Automation hat read error: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
            if automationhat.input[2].read() == 1:
                try:
                    if previous_two != True:
                        bay_watch.button_change(2, 'CLOSED')

                except Exception as e:
                    bay_watch.logger.exception('%s - Function call failed for input %s: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '2', e))

                previous_two = True
            elif automationhat.input[2].read() == 0:
                try:
                    if previous_two != False:
                        bay_watch.button_change(2, 'OPEN')

                except Exception as e:
                    bay_watch.logger.exception('%s - Function call failed for input %s: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '2', e))

                previous_two = False
            else:
                bay_watch.logger.exception('Automation hat read error: %s \n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

            time.sleep(float(bay_watch.config_dict['sleep_time']))
    except KeyboardInterrupt:
        bay_watch.logger.info('BayWatch.py stop. %s ' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

