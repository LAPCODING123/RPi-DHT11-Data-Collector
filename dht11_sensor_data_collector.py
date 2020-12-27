#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to test if the DHT 11 Sensor works
Author: Lorenzo Pedroza
Date 12/15/2020
"""

import adafruit_dht
import time
import sys
import gpiozero
import csv
import pushbullet
import os

DHT_SENSOR = None
BUZZER = None
push_bullet = pushbullet.PushBullet(os.environ['PUSHBULLET_API_ACCESS_TOKEN']) #access token
my_phone = push_bullet.get_device(os.environ['PUSHBULLET_API_PHONE_NAME'])


SAMPLE_TIME = None #seconds
SAMPLES_NEEDED = None
USE_PUSH_BULLET = False
start_time = None
end_time = None

def start_tone():
    #start tone
    global BUZZER
    BUZZER.play(gpiozero.tones.Tone('G5'))
    time.sleep(0.5)
    BUZZER.stop()
    time.sleep(0.1)
    BUZZER.play(gpiozero.tones.Tone('A5'))
    time.sleep(0.3)
    BUZZER.stop()

def sensor_error_tone():
    global BUZZER
    BUZZER.play(gpiozero.tones.Tone('F4'))
    time.sleep(0.5)
    BUZZER.stop()
    time.sleep(0.1)
    BUZZER.play(gpiozero.tones.Tone('B4'))
    time.sleep(0.3)
    BUZZER.stop()

def file_error_tone():
    global BUZZER
    BUZZER.play(gpiozero.tones.Tone('C4'))
    time.sleep(0.5)
    BUZZER.stop()
    time.sleep(0.1)
    BUZZER.play(gpiozero.tones.Tone('C4'))
    time.sleep(0.3)
    BUZZER.stop()

def done_tone():
    #start tone
    global BUZZER
    BUZZER.play(gpiozero.tones.Tone('F5'))
    time.sleep(0.5)
    BUZZER.stop()
    time.sleep(0.1)
    BUZZER.play(gpiozero.tones.Tone('A3'))
    time.sleep(0.3)
    BUZZER.stop()

def main():
    if len(sys.argv) != 7:
        sys.exit('Usage python dht11_sensor_data_collector.py <outfile.csv> <amount of sample to collect>\
                 <time to run (in minutes)> <sensor pin> <speaker pin> <use Pushbullet (-y or -n)>')
    
    global BUZZER
    global DHT_SENSOR
    global start_time
    global end_time
    global USE_PUSH_BULLET
  
    outfile_name = sys.argv[1]
    SAMPLES_NEEDED = int(sys.argv[2])  
    #convert time given in minutes to seconds
    TIME_TO_RUN = float(sys.argv[3])*60
    SAMPLE_FREQUENCY = TIME_TO_RUN/SAMPLES_NEEDED
    dht_pin = int(sys.argv[4])
    DHT_SENSOR = adafruit_dht.DHT11(dht_pin)
    buzzer_pin = int(sys.argv[5])
    BUZZER = gpiozero.TonalBuzzer(buzzer_pin)
    USE_PUSH_BULLET = True if sys.argv[6] == '-y' else False    

    #due to python stuff I guess, not always going to get reading
    try:
        outfile = open(outfile_name, 'w')
        writer = csv.writer(outfile)
        writer.writerow(('Date', 'Time', 'Temperatre (C)', 'Relative Humidity (%)'))
        
        start_tone()#program succesfully started
        print(f'Samples to Collect: {SAMPLES_NEEDED}, Time to run {TIME_TO_RUN/60}min, Sample Frequency: {SAMPLE_FREQUENCY}s')
        start_time = f"{time.strftime('%H:%M:%S')} {time.strftime('%D')}"
        if USE_PUSH_BULLET:
            my_phone.push_note('Temp and Humidity Test', 'Started')
        
        samples = 0
        while samples < SAMPLES_NEEDED:
            try:
                humidity, temperature = DHT_SENSOR.humidity, DHT_SENSOR.temperature
                print(f"Sample# {samples+1} {time.strftime('%H:%M:%S')} {time.strftime('%D')} Temp={temperature}C   Humidity={humidity}%", end='\r')
                #f'Time={time.strftime('%D')} {time.strftime('%H:%M:%S')}  Temp={temperature}C   Humidity={humidity}%'
                writer.writerow((time.strftime('%D'), time.strftime('%H:%M:%S'), temperature, humidity))
                samples += 1
            
            except RuntimeError as error:
                if error.args[0] == 'DHT sensor not found, check wiring':
                    sensor_error_tone()
                    print('\nSensor failure. Check wiring.')
                    if USE_PUSH_BULLET:
                        my_phone.push_note('Temp and Humidity Test', 'Sensor failure check wirring')
                        
            end_time = f"{time.strftime('%H:%M:%S')} {time.strftime('%D')}"
            time.sleep(SAMPLE_FREQUENCY)

        print('\nFinished succesfully')
        if USE_PUSH_BULLET:
            my_phone.push_note('Temp and Humidity Test', 'Done')
        done_tone()

    except IOError:
        file_error_tone()
        print(f'Could not open {outfile_name}')

    except KeyboardInterrupt:
        print(f'\nProgram stopped by user')

    finally:
        if DHT_SENSOR: #if sensor started
            DHT_SENSOR.exit()
        if outfile: #if file was made
            outfile.close()
        if start_time and end_time:
            print(f'{samples} samples recorded in {outfile_name}, Started {start_time}, Finished {end_time}')

if __name__ == "__main__":
    main()
