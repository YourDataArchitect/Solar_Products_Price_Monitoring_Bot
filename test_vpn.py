from tabulate import tabulate
import logging
import concurrent.futures
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time 
import subprocess
import os 
import undetected_chromedriver as uc
import locale
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import gspread
import pytz
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from google.oauth2 import service_account
import os 
import time
from datetime import datetime,timedelta
import pandas as pd 
from googleapiclient.discovery import build
import scrapy 
import random 
import subprocess
import gzip
import io
from scrapy.exceptions import NotConfigured
import mysql.connector
from mysql.connector import Error
import threading

class IP_Rotations:
    # Reference : https://support.surfshark.com/hc/en-us/articles/360011051133-How-to-set-up-manual-OpenVPN-connection-using-Linux-Terminal

    # openvpn credintials (auth.txt) : 
    # user : KwWYP9wAp2cFGeCQVb7TAKUx
    # pass : MhvswcwyUrd6bzTpkFzhnLfy

    # for running docker image for vpn rotations you should use :
    # docker run --dns=8.8.8.8 --cap-add=NET_ADMIN --device=/dev/net/tun --name=auto_vpn -it auto_vpn:v1
    

    def setup_connection():
        # Update and install wireguard and unzip the configurations files
        try:
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'wireguard', 'unzip'], check=True)
            
            # Download the Surfshark configuration files for WireGuard
            subprocess.run(['wget', 'https://my.surfshark.com/vpn/api/v1/server/configurations/wg', '-O', 'wireguard_config.zip'], check=True)
            
            # Unzip the downloaded configuration files
            subprocess.run(['unzip', 'wireguard_config.zip'], check=True)
            
            # You will need to manually set up the WireGuard configuration here
            # Assuming you have a WireGuard config file (wg0.conf), you can run it using wg-quick
            
            # This assumes the configuration file is named wg0.conf and is in the current directory
            subprocess.run(['wg-quick', 'up', './wg0.conf'], check=True)
            
        except subprocess.CalledProcessError as e:
            print("WireGuard setup failed")
            print(f"Error: {e}")


            
    def berlin_connection():
        # Start OpenVPN using the specific configuration file
        process = subprocess.Popen(['openvpn', '--config', '/app/de-ber.prod.surfshark.com_tcp.ovpn', '--auth-user-pass', 'auth.txt'])
        return process 

    def frankfourth_connection():   
        process = subprocess.Popen(['openvpn', '--config', '/app/de-fra.prod.surfshark.com_tcp.ovpn', '--auth-user-pass', 'auth.txt'])
        return process 

    def terminate_connection(process):
        process.terminate()
        print(f'\n---->>> Connection Terminated \n' )
        
    def get_ip_address():
        result = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True)
        print(f'\n---->>> Current IP :: {result.stdout}\n' )
            
    def wait_time(sec):
        list_allowd_secounds = [x for x in range(0,sec,10)] # this list for print message every 10 secounds
        for i in range(sec):
            time.sleep(1)
            if i in list_allowd_secounds:
                print(f'\n\nRemining Time for swich IP ({sec-i}) secounds')
                IP_Rotations.get_ip_address()
                

    def rotation_manger():
        # IP_Rotations.berlin_connection()
        IP_Rotations.frankfourth_connection()
        IP_Rotations.wait_time(14000)
        # # IP_Rotations.frankfourth_connection()
        # # IP_Rotations.wait_time(12000)
        # for _ in range(20):  # for IP Rotation for every 10 minutes - 3 hours
        #     print('************') 
        #     process = IP_Rotations.berlin_connection()
        #     IP_Rotations.wait_time(600)
        #     IP_Rotations.terminate_connection(process)
   
   
   
IP_Rotations.setup_connection()