#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to test if the DHT 11 Sensor works
Author: Lorenzo Pedroza
Date 12/28/2020
"""

import time
import sys
import csv
import os
import gpiozero
import adafruit_dht
import pushbullet

 #These values are globally accessbile
push_bullet = pushbullet.PushBullet(os.environ['PUSHBULLET_API_ACCESS_TOKEN']) #access token
my_phone = push_bullet.get_device(os.environ['PUSHBULLET_API_PHONE_NAME'])

def play_start_tone(buzzer: gpiozero.TonalBuzzer):
    """Plays the program start tone on the buzzer

    Args:
        buzzer (gpiozero.TonalBuzzer): The buzzer to play the tone with
    """
    buzzer.play(gpiozero.tones.Tone('G5'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('A5'))
    time.sleep(0.3)
    buzzer.stop()

def play_sensor_error_tone(buzzer: gpiozero.TonalBuzzer):
    """Plays the program sensor error tone on the buzzer

    Args:
        buzzer (gpiozero.TonalBuzzer): The buzzer to play the tone with
    """
    buzzer.play(gpiozero.tones.Tone('F4'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('B4'))
    time.sleep(0.3)
    buzzer.stop()

def play_file_error_tone(buzzer: gpiozero.TonalBuzzer):
    """Plays the program file error tone on the buzzer

    Args:
        buzzer (gpiozero.TonalBuzzer): The buzzer to play the tone with
    """
    buzzer.play(gpiozero.tones.Tone('C4'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('C4'))
    time.sleep(0.3)
    buzzer.stop()

def play_done_tone(buzzer: gpiozero.TonalBuzzer):
    """Plays the program done tone on the buzzer

    Args:
        buzzer (gpiozero.TonalBuzzer): The buzzer to play the tone with
    """
    buzzer.play(gpiozero.tones.Tone('F5'))
    time.sleep(0.5)
    buzzer.stop()
    time.sleep(0.1)
    buzzer.play(gpiozero.tones.Tone('A3'))
    time.sleep(0.3)
    buzzer.stop()

def collect_sample(dht_sensor: adafruit_dht.DHTBase, writer: csv.writer, next_sample_number: int):
    """Records the values of the dht sensor using a csv _writer. Prints result to console

    Args:
        dht11_sensor (adafruit_dht.DHTBase): The DHT sensor
        writer (csv.writer): The csv.writer to record the sensor data
    """
    humidity, temperature = dht_sensor.humidity, dht_sensor.temperature
    print(f"Sample# {next_sample_number} {time.strftime('%H:%M:%S')} {time.strftime('%D')}"
          f"Temp={temperature}C   Humidity={humidity}%", end='\r')
    writer.writerow((time.strftime('%D'),
                     time.strftime('%H:%M:%S'),
                     temperature,
                     humidity))

def notify_failure(buzzer: gpiozero.TonalBuzzer, use_pushbullet: bool):
    """Notifies user via buzzer, termianl message, and phone if specified of failure

    Args:
        buzzer (gpiozero.TonalBuzzer): The buzzer to play the tone with
        use_pushbullet (bool): Whether to notify user with pushbullet
    """
    play_sensor_error_tone(buzzer)
    print('\nSensor failure. Check wiring.')
    if use_pushbullet:
        my_phone.push_note('Temp and Humidity Test', 'Sensor failure check wirring')

def notify_done(buzzer: gpiozero.TonalBuzzer, use_pushbullet: bool):
    """Notifies user via buzzer, termianl message, and phone if specified of failure

    Args:
        buzzer (gpiozero.TonalBuzzer): The buzzer to play the tone with
        use_pushbullet (bool): Whether to notify user with pushbullet
    """
    play_done_tone(buzzer)
    print('\nFinished succesfully')
    if use_pushbullet:
        my_phone.push_note('Temp and Humidity Test', 'Done')

def main():
    """The main program"""
    if len(sys.argv) != 7:
        sys.exit('Usage python dht11_sensor_data_collector.py <outfile_name.csv>'
                 ' <amount of sample to collect> <time to run (in minutes)>'
                 ' <sensor pin> <speaker pin> <use Pushbullet (-y or -n)>')

    outfile_name = sys.argv[1]
    samples_needed = int(sys.argv[2])
    #convert time given in minutes to seconds
    time_to_run = float(sys.argv[3])*60
    sample_frequency = time_to_run/samples_needed
    dht11_pin = int(sys.argv[4])
    dht11_sensor = adafruit_dht.DHT11(dht11_pin)
    buzzer_pin = int(sys.argv[5])
    buzzer = gpiozero.TonalBuzzer(buzzer_pin)
    use_push_bullet = sys.argv[6] == '-y'
    start_time = None
    end_time = None
    outfile = None

    try:
        #Initialize File Recording
        outfile = open(outfile_name, 'w')
        writer = csv.writer(outfile)
        writer.writerow(('Date', 'Time', 'Temperatre (C)', 'Relative Humidity (%)'))
        #Notify user of program start
        play_start_tone(buzzer)
        print(f"Samples to Collect: {samples_needed}, Time to run {time_to_run/60}min, "
              f"Sample Frequency: {sample_frequency}s")
        start_time = f"{time.strftime('%H:%M:%S')} {time.strftime('%D')}"
        if use_push_bullet:
            my_phone.push_note('Temp and Humidity Test', 'Started')
        #Collect samples
        samples = 0
        while samples < samples_needed:
            try:
                collect_sample(dht11_sensor, writer, samples+1)
                samples += 1

            except RuntimeError as error:
                if error.args[0] == 'DHT sensor not found, check wiring':
                    notify_failure(buzzer, use_push_bullet)

            end_time = f"{time.strftime('%H:%M:%S')} {time.strftime('%D')}"
            time.sleep(sample_frequency)
        #Notify user of program completion
        notify_done(buzzer, use_push_bullet)

    except IOError:
        play_file_error_tone(buzzer)
        print(f'Could not open {outfile_name}')

    except KeyboardInterrupt:
        print('\nProgram stopped by user')

    finally:
        dht11_sensor.exit()
        if outfile: #if file was made
            outfile.close()
        if start_time and end_time:
            print(f"{samples} samples recorded in {outfile_name}"
                  f" Started {start_time}, Finished {end_time}")

if __name__ == "__main__":
    main()
