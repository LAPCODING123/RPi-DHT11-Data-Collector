# RPi-DHT11-Data-Collector
*by Lorenzo Pedroza*

A Python Script for the Raspberry Pi that collects data from a DHT11 Sensor and logs the output in a CSV file. It notifies the user of events such as sensor failure using the PushBullet API.

*The below shell examples are for a Debian Buster installation. Please refer to the below links or the documentation for your specific distro/os*.

## Prerequisites
1. [Have an installation of `pipenv`](https://pypi.org/project/pipenv/) (`$ sudo apt install pipenv`)
2. Install `libgpiod2` (`$ sudo apt install libgpiod2`)

## Setup
1. Clone this repository and change into its directory.
2. Run `$ pipenv install` to install dependencies.
3. Copy `.env_sample` and rename it to `.env`.
    1. Create a Pushbullet access token [(find it in Account Settings)](https://www.pushbullet.com/#settings/account) and add it where specified in the `.env` file (Make a PushBullet acount if you don't have on already). ***Never publish sensitive informaiton like API tokens on public sites like GitHub. The `.gitignore` file prevents Git from committing the `.env` file for this reason***
    2. Download the PushBullet app on the device you would like to recieve notifcations on. Sign in to the same account. Make note of the name of the device on your account. 
    2. Add the name of the device you intend to send notications where specified in `.env` file.

## Usage
1. `$ pipenv run python dht11_sensor_data_collector.py <outfile_name.csv> <amount of sample to collect> <time to run (in minutes)> <sensor pin> <speaker pin> <use Pushbullet (-y or -n)>`

### Example
    $ pipenv run python dht11_sensor_data_collector.py test.csv 10 2 21 18 -y
    Loading .env environment variables…
    Samples to Collect: 10, Time to run 2.0min, Sample Frequency: 12.0s
    Sample# 1 09:55:33 12/27/20 Temp=23C   Humidity=37%
    Finished succesfully
    De-initializing self.pulse_in
    10 samples recorded in test.csv, Started 09:55:33 12/27/20, Finished 09:57:36 12/27/20
 
 *This fourth line in te above snippet updates to show the last sample collected*
 
 2. Use `Ctrl+c` or the equivalent to invoke a `Keyboard Interrupt` to manually stop the program.
 3. If a sensor failure occurs you will be notified on Pushbullet and in the shell.
