#!/usr/bin/python3.7

import automationhat
import os
import ST7735 as ST7735
import sys
import time

from fonts.ttf import RobotoBlackItalic as UserFont
from gpiozero import CPUTemperature
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

if __name__ == "__main__":
    # Initialize display variables
    color = (255, 255, 255)
    font = ImageFont.truetype(UserFont, 12)

    disp = ST7735.ST7735(
        port=0,
        cs=ST7735.BG_SPI_CS_FRONT,
        dc=9,
        backlight=25,
        rotation=270,
        spi_speed_hz=4000000
    )

    # Values to keep everything aligned nicely.
    text_x = 10
    text_y = 10

    try:
        while True:
            # Value to increment for spacing text and bars vertically.
            offset = 0

            # Open our background image.
            image = Image.open(Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images/inputs-blank.jpg')))
            draw = ImageDraw.Draw(image)

            # Draw the temperature
            cpu = CPUTemperature()
            draw.text((text_x, text_y + offset), "CPU Temp: {temp:.2f}".format(temp=cpu.temperature), font=font, fill=color)
            offset += 14

            #Read channels into image and display
            for channel in range(3):
                reading = automationhat.input[channel].read()
                draw.text((text_x, text_y + offset), "{channel:.0f} input reads: {reading:.2f}".format(channel=channel, reading=reading), font=font, fill=color)
                offset += 14

            # Draw the image to the display.
            disp.display(image)

            image.close()

            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nExiting")