#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to test if the DHT 11 Sensor works
Author: Lorenzo Pedroza
Date 12/15/2020
"""

import Adafruit_DHT
import time
import sys
import gpiozero
import csv
import pushbullet

DHT_SENSOR = Adafruit_DHT.DHT11
buzzer = gpiozero.TonalBuzzer(3)
DHT_PIN = 21
push_bullet = pushbullet.PushBullet("o.dR0GIQscwThkLY9KyY3hQ96wE3NHCO0y") #access token
my_phone = push_bullet.get_device('Motorola Moto g stylus')


SAMPLE_TIME = 3 #seconds

SAMPLES_NEEDED = 20

FAILURE_THRESHOLD = 5 # 5 consectutive failed readings

start_time = None
end_time = None

def start_tone():
    #start tone
    buzzer.play(gpiozero.tones.Tone('G5'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('A5'))
    time.sleep(0.3)
    buzzer.stop()

def sensor_error_tone():
    buzzer.play(gpiozero.tones.Tone('F4'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('B4'))
    time.sleep(0.3)
    buzzer.stop()

def file_error_tone():
    buzzer.play(gpiozero.tones.Tone('C4'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('C4'))
    time.sleep(0.3)
    buzzer.stop()

def done_tone():
    #start tone
    buzzer.play(gpiozero.tones.Tone('F5'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('A3'))
    time.sleep(0.3)
    buzzer.stop()

def main():
    failure_count = 0
    outfile_name = sys.argv[1]

    if sys.argv[2]: #if another arg
        SAMPLES_NEEDED = int(sys.argv[2])
    
    if sys.argv[3]:  #in minutes
        TIME_TO_RUN = float(sys.argv[3])*60

    SAMPLE_FREQUENCY = TIME_TO_RUN/SAMPLES_NEEDED

    #due to python stuff I guess, not always going to get reading
    try:
        outfile = open(outfile_name, 'w')
        writer = csv.writer(outfile)
        writer.writerow(('Date', 'Time', 'Temperatre (C)', 'Relative Humidity (%)'))
        start_tone()#program succesfully started
        print(f'Samples to Collect: {SAMPLES_NEEDED}, Time to run {TIME_TO_RUN/60}min, Sample Frequency: {SAMPLE_FREQUENCY}s')
        start_time = f"{time.strftime('%H:%M:%S')} {time.strftime('%D')}"
        samples = 0
        while samples < SAMPLES_NEEDED:
            humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
            if humidity and temperature: #if there is a humidity and temperature
                print(f"Sample# {samples+1} {time.strftime('%H:%M:%S')} {time.strftime('%D')} Temp={temperature}C   Humidity={humidity}%", end='\r')
                failure_count = 0 #reset failure count
                #f'Time={time.strftime('%D')} {time.strftime('%H:%M:%S')}  Temp={temperature}C   Humidity={humidity}%'
                writer.writerow((time.strftime('%D'), time.strftime('%H:%M:%S'), temperature, humidity))
                samples += 1
            else:
                if failure_count >= FAILURE_THRESHOLD:
                    sensor_error_tone()
                    if failure_count == FAILURE_THRESHOLD:
                        print('\nSensor failure. Check wiring.')
                    if failure_count%FAILURE_THRESHOLD == 0: #send error message
                        my_phone.push_note('Temp and Humidity Test', 'Sensor failure check wirring')
                failure_count += 1
                #sys.exit('Sensor failure. Check wiring.')
            end_time = f"{time.strftime('%H:%M:%S')} {time.strftime('%D')}"
            time.sleep(SAMPLE_FREQUENCY)
        print('\nFinished succesfully')
        my_phone.push_note('Temp and Humidity Test', 'Done')
        done_tone()

    except IOError:
        file_error_tone()
        print(f'Could not open {outfile_name}')

    except KeyboardInterrupt:
        print(f'\nProgram stopped by user')

    finally:
        if outfile: #if file was made
            outfile.close()
        if start_time and end_time:
            print(f'{samples} samples recorded in {outfile_name}, Started {start_time}, Finished {end_time}')

if __name__ == "__main__":
    main()
