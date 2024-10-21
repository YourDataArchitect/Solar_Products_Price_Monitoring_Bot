from tabulate import tabulate
import logging
import concurrent.futures
import time
from googleapiclient.errors import HttpError
from httplib2 import ServerNotFoundError
from requests.exceptions import Timeout, ConnectionError
import smtplib
from mysql.connector import errors
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
import socket
import random 
import gzip
import ssl
import io
from scrapy.exceptions import NotConfigured
import mysql.connector
from mysql.connector import Error
import threading
import pymysql


# Global variable
warning_list = []

def retry_decorator(func):
    "This function for handel target function with unstable connections"
    def wrapper(*args, **kwargs):
        for i in range(70): # for wait 180 seconds (3 minutes)
            try : 
                result = func(*args, **kwargs)
                return result 
            except (HttpError,pymysql.MySQLError, ServerNotFoundError , ssl.SSLError,socket.error, TimeoutError , Timeout , ConnectionError , errors.InterfaceError , errors.DatabaseError) as e:
                print(f"Attempt {i} failed: {e}")
                time.sleep(5)
        raise Exception("After 3 minutes, the retry attempt failed.\nReason unstable connection .")
    return wrapper
        
class IP_Rotations:
    # Reference : https://support.surfshark.com/hc/en-us/articles/360011051133-How-to-set-up-manual-OpenVPN-connection-using-Linux-Terminal

    # openvpn credintials (auth.txt) : Normal connection
    # user : KwWYP9wAp2cFGeCQVb7TAKUx
    # pass : MhvswcwyUrd6bzTpkFzhnLfy

    # openvpn credintials (auth.txt) : dedicated ip
    # user : EQzbhWRXNjpxR3EtDr6BwU6x
    # pass : K2auXNvAUG6nKMX8jSFG7UsW

    # for running docker image for vpn rotations you should use :
    # docker run --dns=8.8.8.8 --cap-add=NET_ADMIN --device=/dev/net/tun --name=auto_vpn -it auto_vpn:v1
    
    def setup_connection():
        # Update and install openvpn and unzip the configirations files 
        try : 
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'openvpn', 'unzip'], check=True)
            
            # Download the Surfshark configuration files
            subprocess.run(['wget', 'https://my.surfshark.com/vpn/api/v1/server/configurations', '-O', 'configurations.zip'], check=True)
            
            # Unzip the downloaded configuration files
            subprocess.run(['unzip', 'configurations.zip'], check=True)
        except subprocess.CalledProcessError as e :
            print("file setup_vpn.py failed")
            print(f"error {e}")
            

            
    def berlin_connection(original_ip):
        # Start OpenVPN using the specific configuration file
        print('-- >>> Connect Berlin server ')
        process = subprocess.Popen(['openvpn', '--config', '/app/de-ber.prod.surfshark.com_tcp.ovpn', '--auth-user-pass', 'auth.txt'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # process = subprocess.Popen([r"C:\Users\Ramz\Desktop\scrapy_projects\robin\market_monitor_with_vpn\openvpn-portable\openvpn-portable.exe", '--config', r"C:\Users\Ramz\Desktop\scrapy_projects\robin\market_monitor_with_vpn\de-ber.prod.surfshark.com_tcp.ovpn", '--auth-user-pass', r"C:\Users\Ramz\Desktop\scrapy_projects\robin\market_monitor_with_vpn\auth.txt"],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Read the output line by line and print it to the terminal
        logs = []
        counter_secounds = 0
        while True:
            output = process.stdout.readline()
            if 'Initialization Sequence Completed' in output:
                print("-->>> Initialization Sequence Completed. VPN connection is now stable.")
                return 'True'
                
                
            else :
                if counter_secounds >= 180 : # wait 180 secounds untill the connection is stable
                    return process # return process for terminated connection
                else :
                    log_message = output.strip()
                    logs.append(log_message)
                    print(log_message)
                    counter_secounds += 1
                    # print('Processing counter secounds',counter_secounds)
                    time.sleep(0.1)

    def frankfourth_connection(original_ip):
        print('-- >>> Connect Frankfourt server ')   
        process = subprocess.Popen(['openvpn', '--config', '/app/de-fra.prod.surfshark.com_tcp.ovpn', '--auth-user-pass', 'auth.txt'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # Read the output line by line and print it to the terminal
        logs = []
        counter_secounds = 0
        while True:
            output = process.stdout.readline()
            if 'Initialization Sequence Completed' in output:
                "-->>> Initialization Sequence Completed. VPN connection is now stable."
                break
                
                
            else :
                if counter_secounds >= 180 : # 1800 wait 180 secounds untill the connection is stable
                    warning_list = [f'Warning: Your IP address ({original_ip}) is exposed to other servers, and the VPN is not available.'] 
                    Tools.sending_email('warning',warning_list)
                    break
                else :
                    log_message = output.strip()
                    logs.append(log_message)
                    print(log_message)
                    counter_secounds += 1
                    print('line 140',counter_secounds)
                    time.sleep(0.1) 
                    
                    
 
    
    def deducated_ip_connection():   
        process = subprocess.Popen(['openvpn', '--config', '/app/de-fra.prod.surfshark.comsurfshark_openvpn_tcp.ovpn', '--auth-user-pass', 'auth_Dedicated.txt'])
        return process 



    def terminate_connection(process):
        process.terminate()
        print(f'\n---->>> Connection Terminated \n' )
        
    def get_ip_address():
        result = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True)
        return result.stdout
            
    def Monitor_IP(original_ip):
        running_seconds  = 1260 # roughly_seconds = 12,600 seconds ~= 3.5 hours
        list_allowed_seconds  = [x for x in range(0,running_seconds ,360)] # this list for print message every 60 Minutes
        
        for i in range(running_seconds):
            current_ip = IP_Rotations.get_ip_address().strip()
            time.sleep(10)
            print(f'\n\nOriginal IP ({original_ip}) \nCurrent IP ({current_ip})')
            if i in list_allowed_seconds :
                if original_ip != current_ip:
                    warning_list = [f'Warning: Your IP address ({original_ip}) is exposed to other servers, and the VPN is not available.'] 
                    Tools.sending_email('warning',warning_list)


    def rotation_manger_berlin_frnkfourt():
        original_ip = IP_Rotations.get_ip_address().strip()
        print(f'-->>> Original IP Address : {original_ip}')
        process = IP_Rotations.berlin_connection(original_ip)
        print(f'Line 180 {process}')
        if process != 'True' : 
            print('******** Berlin connection is Faild and Will try frankfourt server ')
            IP_Rotations.terminate_connection(process)
            IP_Rotations.frankfourth_connection(original_ip)
        
        IP_Rotations.Monitor_IP(original_ip)

    def rotation_manger_deducted_ip():
        original_ip = IP_Rotations.get_ip_address().strip()
        print(f'-->>> Original IP Address : {original_ip}')
        IP_Rotations.deducated_ip_connection()
        IP_Rotations.Monitor_IP(original_ip)
            
        
            

class TimeoutException(Exception):
    pass


class sorting_new_products_sheet:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = {
            "type": "service_account",
            "project_id": "astute-charter-425618-q7",
            "private_key_id": "f97df6dbdb34806e8c1d73ee6425800be96d50c5",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsdr4KnB0pYOXp\n9j/tGk8a5uAbMcfgb3+avO67BywEcBNx519qV3zTecvh/nr2YksG8MFBxmI3yj3P\n1HKfMMjPUfUriOM5eEKJcwvJqfrTbACzRjHkiY29gBjA8L5AnGYMwEWN3ha6RJy6\nMAYfNbSwzpGrHPby7I/6Fnee06H3rZ/+xNZfcQzPZCJsUOWbE/mZlAx4Zj3NiIb+\nnUULzIhZIPdBcBs8YW132cpCLzcFFPWRzdhA+bSiQm3G1jcrZY3H8lq6JHas+7bT\nRzXz9FQ7epRCp/MSsbcuya/FUo+CyM9PwX6JKxHw++7EzSTpPN0paLTaA/Iq2SxT\nSQDTvNdpAgMBAAECggEAKtbH9+y1VazrD0WKtYOeeKk2q6qe4oHvqWkax7xNU8Df\nI6D8U3bt273aRgWnV4Is7slox8TWatNCrVgxLJe6mbza8HhtML5NkMTR/cLKOjAO\nsHlUNVdxrMuf2nUyXOw8cRhlbornDFe0so7xRllZy71T87QbJ1ZZoR5pkjsxdUr0\nC9bzcZUcEBBtjaF93JfsF6XAvjSsYH6/ZQduqNuN6BX6dO6ZO9+Cbq8uOR+VXbKq\nogdgGOMXX86t1EbDvB50duv/kdj+dYsyaSKL2laKQr/GLwrBSMFvwEZLs5GxmOwe\nfO7+BDi3nv05LyTDseAJdkGocbWKXMV6bwBAjTgH8QKBgQDZUuBAJxfVvTxbwc4r\nUJr4RsVkRT9pxth7YDszxgjNgJTR0HPaPSDCSEX4QwhbWatZy+bPXFuJlMN53Tpz\njzXfszyMlJhM2eLC3ROSNmaA2tCed9FdEJqSFaKhe2e64vC3PCuW7b0nvPgkdyoO\nMzTKHbtmlmynHck5KJbWy+d1TQKBgQDLKBRXbzUBFOJKMhDxpPJNlaTuLiDsAVrM\nMzr2XHQZJLGInAqr/OXU70voYqrmV8xMXNaheeZUZbuAtMa2Bl0eS02FFkzky7Iv\nip9QcVs9/myld8qVAmjJAzrm8ejcuq1AJRy9BLOxT9oVLwUQGJ7lIy9k4z1HFU4c\nVE+yRXgsjQKBgD2tr8eFUNZwprjEAGd6sQDV1R/oJ181+CrL3QGMquLoI1SI/Nhr\nkOiS6ojTPYPvpxoNLKydYb1iYzgq+XPiqT+b9wtPAQqOrDTx2aQdnGnlsF/JUbpA\nBB6B1W5PP9linz7h7N0hDBZDI4n16BGvpsPWPGGZP60OXxXB102PAVnhAoGAZB91\nnv3MxqKvP9fa5+zeCgSlS0lqqkWkpRzeg0pfYYDnCie1TrwN3VquM3JlPa6pnjzm\n/qAgNxoIRc9SW6VZQTPlmaC69su5HpsYF0I2sJ/ylb4rFjMgx2iTH/y7QgWymvlv\nZ2yozstG9Me+nAc2UEF9+x/PNHg4jdezi22XY4UCgYEAylTRauWSC4wYiwC73NcM\nHeMnvj1wGXhBFRcdyOH1hrCCofkcs7am5OGIwjRTXj2Pe4rCZvLFG2aSWAGzYeL3\nLAC8K+Z1dGI5OcPg8t1sJ+4yqO1IP4452eHlNB5/09Bk/1IU9/64wBTIwxMGW3Z+\nwJzVDKS8gHHgOro7DlC7sSE=\n-----END PRIVATE KEY-----\n",
            "client_email": "sheets@astute-charter-425618-q7.iam.gserviceaccount.com",
            "client_id": "116398454531310558463",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets%40astute-charter-425618-q7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"}
        self.SPREADSHEET_ID = '1EVJWvK17OUnG4wEd3TuRVhTQTindyEgCsLoOviQjOOY' 
        
        
    def read_google_sheet_new_products(self):
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_info(self.SERVICE_ACCOUNT_FILE, scopes=self.scopes)
        
        # Authorize the client
        client = gspread.authorize(credentials)
        
        sheet = client.open_by_key(self.SPREADSHEET_ID).worksheet('Neue_Produkte') # or use sheet number
        # Read data from the specified range
        cell_range = sheet.get('A7:F10000')
        
        # Convert the cell range to a list of dictionaries, assuming the first row is the header
        headers = cell_range[0]
        data = [dict(zip(headers, row)) for row in cell_range[1:]]
        return data

    def write_data_to_google_sheets(self,df_fresh_data):
        credentials = service_account.Credentials.from_service_account_info(self.SERVICE_ACCOUNT_FILE, scopes=self.scopes)
        service = build('sheets', 'v4', credentials=credentials)
        # Convert DataFrame to list of lists
        list_fresh_records = df_fresh_data.values.tolist()
        body = {'values': list_fresh_records}
        # Write data to the Google Sheets
        service.spreadsheets().values().update(
        spreadsheetId=self.SPREADSHEET_ID,
        range=f"Neue_Produkte!A8",   # change download cell 
        valueInputOption='RAW',
        body=body).execute()        
        
    
    def Main_Sorting(self):
        # # [1] Read all data in the sheet
        extracted_data = self.read_google_sheet_new_products()
        
        # # [2] Sorting data according to update column order
        df = pd.DataFrame(extracted_data)
        
        # # read the column as date 
        df['Update Date'] = pd.to_datetime(df['Update Date'] , format =  '%d.%m.%Y', errors='coerce')
        df['Update Date'] = df['Update Date'].dt.strftime('%Y-%m-%d')
        
        # sorting column 
        df = df.sort_values(by='Update Date',ascending=False)
        df['Update Date'] = pd.to_datetime(df['Update Date']).dt.strftime('%d.%m.%Y')
        
        # [3] Write all thew data after sorting to google sheet 
        self.write_data_to_google_sheets(df)
        print(f'** Sheet (Neue_Produkte) is sorted successfully cells updated.')





class Database_Mangment:
    def __init__(self):
        # Define database config
        current_dirct = os.getcwd()
        file_path = os.path.join(current_dirct,'KEYS.xlsx')
        df = pd.read_excel(file_path , index_col='key')
        
        try : 
            self.connection = mysql.connector.connect(
                host= df.at['host','value'],
                user= df.at['user','value'],
                password= df.at['password','value'],
                database=df.at['database','value'])
            
            print('-- >> Database Connection established Successfully !!! ')
            
            # Create a cursor object to interact with the database
            self.cursor = self.connection.cursor()
            
        except Error as e : 
            warning_list.append(f'Opening Connection Database error: {e} - line 271')
            print(f'Opening Connection Database error: {e}')
        
    @retry_decorator
    def Add_unvalid_url_to_Database_New_products(self,url,source):
        print('-- >> Adding Unvalid LINKS to database')
        # Establish a connection to the MySQL server
        # Iterate through the list of dictionaries and insert each record
        new_dict_for_upload = {}
        new_dict_for_upload['SOURCE'] = source
        new_dict_for_upload['URL'] = url
        new_dict_for_upload['Update_date'] = Tools.current_date_New_products_spider()
        keys_string = ', '.join(new_dict_for_upload.keys())
        values_placeholder = ', '.join(['%s'] * len(new_dict_for_upload))
        values_tuple = tuple(new_dict_for_upload.values())

        insert_query = f'''INSERT INTO sheetsgoogle.New_Products ({keys_string}) VALUES ({values_placeholder})'''
        
        print(f'Insert Record to "New_products" table: {values_tuple}')
        
        self.cursor.execute(insert_query, values_tuple)

        # # # # # Commit the changes to the database
        self.connection.commit()

    @retry_decorator
    def Extract_last_5_prices_from_database(self,URL) -> list[dict]:
        '''This Functuion for get records from the database using the given URL'''
        # get data from database and the output is list of rows
        self.cursor.execute(f'''
                        SELECT * FROM `Follow_Up_Competitors_Prices`
                        WHERE URL = '{URL}';''')
        result_all_data = self.cursor.fetchall()
        self.cursor.execute(f"SHOW COLUMNS FROM `Follow_Up_Competitors_Prices`;")
        columns = self.cursor.fetchall()
        columns
        columns_names = tuple([record[0] for record in columns])
        columns_names
        result_all_data.append(columns_names)
        result_all_data
        list_dicts_records = pd.DataFrame(result_all_data , columns= result_all_data[-1]).to_dict(orient='records')[0]
        list_dicts_records
        if list_dicts_records['Source'] != 'Source':
            columns_list = ['Price_1_day_ago','Price_2_day_ago','Price_3_day_ago','Price_4_day_ago','Price_5_day_ago']
            for column in columns_list:
                if list_dicts_records[column] == None : list_dicts_records[column] = '-'
            
            result = list_dicts_records['Price_1_day_ago'].strip()+', '+list_dicts_records['Price_2_day_ago'].strip()+', '+list_dicts_records['Price_3_day_ago'].strip()+', '+list_dicts_records['Price_4_day_ago'].strip()+', '+list_dicts_records['Price_5_day_ago'].strip()
            result = result.replace('\xa0',' ').replace(' €','')
            return result
        else:
            return '-'
        
    @retry_decorator
    def read_records_NEW_PRODUCTS_database_New_products_spider(self) -> list[dict]:
        '''This Functuion for get records from the database '''
        tableName = 'New_Products'
        self.cursor.execute(f"SELECT URL FROM {tableName}")
        result_all_data = self.cursor.fetchall()
        set_records = {url[0] for url in result_all_data}
        return set_records

    @retry_decorator
    def Add_Records_to_Database_New_products_spider(self,LIST_OF_dicts):
        # INPUT LIST CONTAINS URL'S 
        # Example : input = ['URL_1', 'URL_2', 'URL_3', 'URL_4']
        
        print('-- >> Adding NEW PRODUCTS LINKS to database')

        # Iterate through the list of dictionaries and insert each record
        for record in LIST_OF_dicts:
            # print(record)
            new_dict_for_upload = {}
            new_dict_for_upload['SOURCE'] = record['Source']
            new_dict_for_upload['URL'] = record['URL']
            new_dict_for_upload['Update_date'] = Tools.current_date_New_products_spider()
            keys_string = ', '.join(new_dict_for_upload.keys())
            values_placeholder = ', '.join(['%s'] * len(new_dict_for_upload))
            values_tuple = tuple(new_dict_for_upload.values())

            insert_query = f'''INSERT INTO sheetsgoogle.New_Products ({keys_string}) VALUES ({values_placeholder})'''
            
            print(f'Insert Record to "New_products" table: {values_tuple}')
            self.cursor.execute(insert_query, values_tuple)

        # # # # # Commit the changes to the database
        self.connection.commit()

        
    @retry_decorator
    def check_connection(self):
        try:
            if self.connection.is_connected():
                print("Successfully connected to the database")
                
                # Print the MariaDB server version
                db_info = self.connection.get_server_info()
                print(f"MariaDB server version: {db_info}")
                
                # Create a cursor object
                cursor = self.connection.cursor()
                
                # Execute a simple query
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                print(f"You're connected to database: {record}")
            

        
        except Error as e:
            warning_list.append(f'Error while connecting to MariaDB: {e} - line 207')
            print(f"Error while connecting to MariaDB: {e}")

    @retry_decorator
    def read_records_database(self,tableName) -> list[dict]:
        '''This Functuion for get records from the database '''
        # get data from database and the output is list of rows
        self.cursor.execute(f"SELECT * FROM {tableName}")
        result_all_data = self.cursor.fetchall()
        self.cursor.execute(f"SHOW COLUMNS FROM {tableName};")
        columns = self.cursor.fetchall()
        columns_names = tuple([record[0] for record in columns])
        result_all_data.append(columns_names)
        list_dicts_records = pd.DataFrame(result_all_data , columns= result_all_data[-1]).to_dict(orient='records')
        return list_dicts_records
            
    @retry_decorator
    def Add_Records_to_Database_Follow_Up_Competitors_Prices(self,record,connection,cursor):
        try : 
            # Get keys string
            keys_list = [key for key in record]
            keys_list_after_replace = list(map(lambda x: x.replace('.', '_').replace('Preise','Price') if '2024' or '2025' in x else x , keys_list))
            keys_list_after_replace

            keys_string = ','.join(keys_list_after_replace)
            values_string = ', '.join(['%s'] * len(keys_list))

            # SQL query to insert data into a table
            insert_query = f'''INSERT INTO Follow_Up_Competitors_Prices ({keys_string}) VALUES ({values_string})'''
            
            # Create tuple of values
            data_tuple = tuple(record.values())
            data_tuple
            # If any value is a string, replace '.' with '_'

            # Execute the query
            cursor.execute(insert_query, data_tuple)
            
            # Commit the changes to the database
            connection.commit()
            
            
        except mysql.connector.Error as err:
            warning_list.append(f'MySQL Error: {err} - line 300')
            print(f"Error: {err}")
        except Exception as e:
            warning_list.append(f'MySQL Error: {err} - line 303')
            print(f"Exception: {e}")
            

    @retry_decorator
    def extract_record_from_database_using_url(self,tableName,URL) -> list[dict]:
        '''This Functuion for get records from the database using the given URL'''
        self.cursor.execute(f'''
                        SELECT * FROM `{tableName}`
                        WHERE URL = '{URL}';''')
        result_all_data = self.cursor.fetchall()
        self.cursor.execute(f"SHOW COLUMNS FROM {tableName};")
        columns = self.cursor.fetchall()
        columns_names = tuple([record[0] for record in columns])
        result_all_data.append(columns_names)
        list_dicts_records = pd.DataFrame(result_all_data , columns= result_all_data[-1]).to_dict(orient='records')[0]
        
        # Testing is record is exist in Database or not exist in Database
        if list_dicts_records['Source'] != 'Source':
            return list_dicts_records
        else:
            raise ValueError('Error_Record_not_exist')

    @retry_decorator
    def delete_record_from_database(self,record_url):
        '''This Functuion for Delete all old records according to URL OF RECORD '''
        try :
            self.cursor.execute(f'''
                        DELETE FROM sheetsgoogle.Follow_Up_Competitors_Prices
                        WHERE URL = '{record_url}';''')
            self.connection.commit()
            # print(f'Record Deleted succefully URL : {record_url}')
        except Error as e:
            warning_list.append(f'Error for delete records: {e} - Line 361')
            print(f'Error for delete records : {e}')
            
    @retry_decorator
    def update_column_database(self) -> str :
        '''
        This Functuion for add missing column headers  
        Return : string for current date 
        '''
        self.cursor.execute(f"SHOW COLUMNS FROM sheetsgoogle.Follow_Up_Competitors_Prices;")
        columns = self.cursor.fetchall()
        columns_names_from_database = tuple([record[0] for record in columns])
        new_column_date = Tools.current_date().replace('.','_')
        # check if there all column in record are present in database and if not present create new column
        if new_column_date in columns_names_from_database : 
            pass 
        else : 
            self.cursor.execute(f'''ALTER TABLE `sheetsgoogle`.`Follow_Up_Competitors_Prices` ADD COLUMN `{new_column_date}` Text NULL AFTER `Price_5_day_ago`;''')

    def __del__(self):
        # Close the cursor and connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        
        print("MySQL connection is closed")
    
class BrowserHandler:
    def launch_driver(login_page):
        print(f'-- >> Login page {login_page}')
        # Config Driver Options
        options = uc.ChromeOptions()
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        
        current_dir = os.getcwd()
        download_dir = os.path.join(current_dir, "Downloads")
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        driver_path = os.path.join(os.getcwd(), "chromedriver")
        # Run Driver with arguments
        # LINE 349
        # driver = uc.Chrome(
        #                 use_subprocess=False,
        #                 options=options,
        #                 version_main = 127,
        #                 driver_executable_path = r"D:\scrapy_projects\TOOLS PROJECTS\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe")
        print(f'the driver path = {driver_path}')
        
        driver = uc.Chrome(
                use_subprocess=False,
                options=options,
                driver_executable_path = driver_path )
        
        driver.get(login_page)
        return driver
        
class Google_sheets:
    @retry_decorator
    def Add_one_Record_to_Database_New_products_spider(SOURCE,URL):
        """this func for insert unvalid product page to database (new product)

        Args:
            list_record
        """
        print("-- >> This product page isn't vsalid so we have to inset to database to not repeat in future")
        print('-- >> Adding NEW PRODUCTS LINKS to database')
        # Establish a connection to the MySQL server
        connection = mysql.connector.connect(
                    host="87.106.82.62",
                    user="Scraper581",
                    password="9?6ndF41j",
                    database="sheetsgoogle")
        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        # Get keys string

        # Iterate through the list of dictionaries and insert each record

        new_dict_for_upload = {}
        new_dict_for_upload['SOURCE'] = SOURCE
        new_dict_for_upload['URL'] = URL
        new_dict_for_upload['Update_date'] = Tools.current_date_New_products_spider()
        keys_string = ', '.join(new_dict_for_upload.keys())
        values_placeholder = ', '.join(['%s'] * len(new_dict_for_upload))
        values_tuple = tuple(new_dict_for_upload.values())

        insert_query = f'''INSERT INTO sheetsgoogle.New_Products ({keys_string}) VALUES ({values_placeholder})'''
        
        print(f'Insert Record to "New_products" table: {values_tuple}')
        cursor.execute(insert_query, values_tuple)

        # # # # # Commit the changes to the database
        connection.commit()
        # # # # Close the cursor and connection
        cursor.close()
        connection.close()
        
    @retry_decorator
    def Get_last_line_Neue_Produkte_sheet():
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        SERVICE_ACCOUNT_FILE = {
            "type": "service_account",
            "project_id": "astute-charter-425618-q7",
            "private_key_id": "f97df6dbdb34806e8c1d73ee6425800be96d50c5",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsdr4KnB0pYOXp\n9j/tGk8a5uAbMcfgb3+avO67BywEcBNx519qV3zTecvh/nr2YksG8MFBxmI3yj3P\n1HKfMMjPUfUriOM5eEKJcwvJqfrTbACzRjHkiY29gBjA8L5AnGYMwEWN3ha6RJy6\nMAYfNbSwzpGrHPby7I/6Fnee06H3rZ/+xNZfcQzPZCJsUOWbE/mZlAx4Zj3NiIb+\nnUULzIhZIPdBcBs8YW132cpCLzcFFPWRzdhA+bSiQm3G1jcrZY3H8lq6JHas+7bT\nRzXz9FQ7epRCp/MSsbcuya/FUo+CyM9PwX6JKxHw++7EzSTpPN0paLTaA/Iq2SxT\nSQDTvNdpAgMBAAECggEAKtbH9+y1VazrD0WKtYOeeKk2q6qe4oHvqWkax7xNU8Df\nI6D8U3bt273aRgWnV4Is7slox8TWatNCrVgxLJe6mbza8HhtML5NkMTR/cLKOjAO\nsHlUNVdxrMuf2nUyXOw8cRhlbornDFe0so7xRllZy71T87QbJ1ZZoR5pkjsxdUr0\nC9bzcZUcEBBtjaF93JfsF6XAvjSsYH6/ZQduqNuN6BX6dO6ZO9+Cbq8uOR+VXbKq\nogdgGOMXX86t1EbDvB50duv/kdj+dYsyaSKL2laKQr/GLwrBSMFvwEZLs5GxmOwe\nfO7+BDi3nv05LyTDseAJdkGocbWKXMV6bwBAjTgH8QKBgQDZUuBAJxfVvTxbwc4r\nUJr4RsVkRT9pxth7YDszxgjNgJTR0HPaPSDCSEX4QwhbWatZy+bPXFuJlMN53Tpz\njzXfszyMlJhM2eLC3ROSNmaA2tCed9FdEJqSFaKhe2e64vC3PCuW7b0nvPgkdyoO\nMzTKHbtmlmynHck5KJbWy+d1TQKBgQDLKBRXbzUBFOJKMhDxpPJNlaTuLiDsAVrM\nMzr2XHQZJLGInAqr/OXU70voYqrmV8xMXNaheeZUZbuAtMa2Bl0eS02FFkzky7Iv\nip9QcVs9/myld8qVAmjJAzrm8ejcuq1AJRy9BLOxT9oVLwUQGJ7lIy9k4z1HFU4c\nVE+yRXgsjQKBgD2tr8eFUNZwprjEAGd6sQDV1R/oJ181+CrL3QGMquLoI1SI/Nhr\nkOiS6ojTPYPvpxoNLKydYb1iYzgq+XPiqT+b9wtPAQqOrDTx2aQdnGnlsF/JUbpA\nBB6B1W5PP9linz7h7N0hDBZDI4n16BGvpsPWPGGZP60OXxXB102PAVnhAoGAZB91\nnv3MxqKvP9fa5+zeCgSlS0lqqkWkpRzeg0pfYYDnCie1TrwN3VquM3JlPa6pnjzm\n/qAgNxoIRc9SW6VZQTPlmaC69su5HpsYF0I2sJ/ylb4rFjMgx2iTH/y7QgWymvlv\nZ2yozstG9Me+nAc2UEF9+x/PNHg4jdezi22XY4UCgYEAylTRauWSC4wYiwC73NcM\nHeMnvj1wGXhBFRcdyOH1hrCCofkcs7am5OGIwjRTXj2Pe4rCZvLFG2aSWAGzYeL3\nLAC8K+Z1dGI5OcPg8t1sJ+4yqO1IP4452eHlNB5/09Bk/1IU9/64wBTIwxMGW3Z+\nwJzVDKS8gHHgOro7DlC7sSE=\n-----END PRIVATE KEY-----\n",
            "client_email": "sheets@astute-charter-425618-q7.iam.gserviceaccount.com",
            "client_id": "116398454531310558463",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets%40astute-charter-425618-q7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
            }
        
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
        
        # Authorize the client
        client = gspread.authorize(credentials)
        SPREADSHEET_ID = '1EVJWvK17OUnG4wEd3TuRVhTQTindyEgCsLoOviQjOOY'  # Your Google Sheets ID

        
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet('Neue_Produkte') # or use sheet number
            # Read data from the specified range
        cell_range = sheet.get('A:A')
        
        # Convert the cell range to a list of dictionaries, assuming the first row is the header
        headers = cell_range[0]
        data = [dict(zip(headers, row)) for row in cell_range[1:]]
        counter_list = [counter for counter in range(len(data)+1)]
        return max(counter_list)+2
    
    @retry_decorator
    def write_NEW_PRODUCTS_to_google_sheets(NEW_PRODUCTS_DATA_FRAME_before):
        # Authenticate and construct service
        SERVICE_ACCOUNT_FILE = {
            "type": "service_account",
            "project_id": "astute-charter-425618-q7",
            "private_key_id": "f97df6dbdb34806e8c1d73ee6425800be96d50c5",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsdr4KnB0pYOXp\n9j/tGk8a5uAbMcfgb3+avO67BywEcBNx519qV3zTecvh/nr2YksG8MFBxmI3yj3P\n1HKfMMjPUfUriOM5eEKJcwvJqfrTbACzRjHkiY29gBjA8L5AnGYMwEWN3ha6RJy6\nMAYfNbSwzpGrHPby7I/6Fnee06H3rZ/+xNZfcQzPZCJsUOWbE/mZlAx4Zj3NiIb+\nnUULzIhZIPdBcBs8YW132cpCLzcFFPWRzdhA+bSiQm3G1jcrZY3H8lq6JHas+7bT\nRzXz9FQ7epRCp/MSsbcuya/FUo+CyM9PwX6JKxHw++7EzSTpPN0paLTaA/Iq2SxT\nSQDTvNdpAgMBAAECggEAKtbH9+y1VazrD0WKtYOeeKk2q6qe4oHvqWkax7xNU8Df\nI6D8U3bt273aRgWnV4Is7slox8TWatNCrVgxLJe6mbza8HhtML5NkMTR/cLKOjAO\nsHlUNVdxrMuf2nUyXOw8cRhlbornDFe0so7xRllZy71T87QbJ1ZZoR5pkjsxdUr0\nC9bzcZUcEBBtjaF93JfsF6XAvjSsYH6/ZQduqNuN6BX6dO6ZO9+Cbq8uOR+VXbKq\nogdgGOMXX86t1EbDvB50duv/kdj+dYsyaSKL2laKQr/GLwrBSMFvwEZLs5GxmOwe\nfO7+BDi3nv05LyTDseAJdkGocbWKXMV6bwBAjTgH8QKBgQDZUuBAJxfVvTxbwc4r\nUJr4RsVkRT9pxth7YDszxgjNgJTR0HPaPSDCSEX4QwhbWatZy+bPXFuJlMN53Tpz\njzXfszyMlJhM2eLC3ROSNmaA2tCed9FdEJqSFaKhe2e64vC3PCuW7b0nvPgkdyoO\nMzTKHbtmlmynHck5KJbWy+d1TQKBgQDLKBRXbzUBFOJKMhDxpPJNlaTuLiDsAVrM\nMzr2XHQZJLGInAqr/OXU70voYqrmV8xMXNaheeZUZbuAtMa2Bl0eS02FFkzky7Iv\nip9QcVs9/myld8qVAmjJAzrm8ejcuq1AJRy9BLOxT9oVLwUQGJ7lIy9k4z1HFU4c\nVE+yRXgsjQKBgD2tr8eFUNZwprjEAGd6sQDV1R/oJ181+CrL3QGMquLoI1SI/Nhr\nkOiS6ojTPYPvpxoNLKydYb1iYzgq+XPiqT+b9wtPAQqOrDTx2aQdnGnlsF/JUbpA\nBB6B1W5PP9linz7h7N0hDBZDI4n16BGvpsPWPGGZP60OXxXB102PAVnhAoGAZB91\nnv3MxqKvP9fa5+zeCgSlS0lqqkWkpRzeg0pfYYDnCie1TrwN3VquM3JlPa6pnjzm\n/qAgNxoIRc9SW6VZQTPlmaC69su5HpsYF0I2sJ/ylb4rFjMgx2iTH/y7QgWymvlv\nZ2yozstG9Me+nAc2UEF9+x/PNHg4jdezi22XY4UCgYEAylTRauWSC4wYiwC73NcM\nHeMnvj1wGXhBFRcdyOH1hrCCofkcs7am5OGIwjRTXj2Pe4rCZvLFG2aSWAGzYeL3\nLAC8K+Z1dGI5OcPg8t1sJ+4yqO1IP4452eHlNB5/09Bk/1IU9/64wBTIwxMGW3Z+\nwJzVDKS8gHHgOro7DlC7sSE=\n-----END PRIVATE KEY-----\n",
            "client_email": "sheets@astute-charter-425618-q7.iam.gserviceaccount.com",
            "client_id": "116398454531310558463",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets%40astute-charter-425618-q7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"}
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  
        credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        SPREADSHEET_ID = '1EVJWvK17OUnG4wEd3TuRVhTQTindyEgCsLoOviQjOOY'  # Your Google Sheets ID

        last_line = Google_sheets.Get_last_line_Neue_Produkte_sheet()
        # Write data to the Google Sheets
        try : NEW_PRODUCTS_DATA_FRAME = NEW_PRODUCTS_DATA_FRAME_before[NEW_PRODUCTS_DATA_FRAME_before['Preise'] != '-']
        except : NEW_PRODUCTS_DATA_FRAME = NEW_PRODUCTS_DATA_FRAME_before
        values_list = NEW_PRODUCTS_DATA_FRAME.values.tolist()
        data_after_foramt = values_list
        body = {'values': data_after_foramt}
        result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"Neue_Produkte!A{last_line}",   # change download cell 
        valueInputOption='RAW',
        body=body).execute()
        
        print(f'** New Products sheet , {result.get("updatedCells")} cells updated.')
        
        
        
        # UPDATE DATA CELL IN [C6]
        cet_tz = pytz.timezone('CET')
        current_date = datetime.now(cet_tz)
        formatted_date = [[f'aktualisiert : {current_date.strftime("%d.%m.%Y - %H:%M")}']]
        body = {'values': formatted_date}
        result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"Neue_Produkte!C6",   # change download cell 
        valueInputOption='RAW',
        body=body).execute()
        
    @retry_decorator
    def write_data_to_google_sheets(df_fresh_data,range_table,list_old_records,sheet_name):

        
        # Authenticate and construct service
        SERVICE_ACCOUNT_FILE = {
            "type": "service_account",
            "project_id": "astute-charter-425618-q7",
            "private_key_id": "f97df6dbdb34806e8c1d73ee6425800be96d50c5",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsdr4KnB0pYOXp\n9j/tGk8a5uAbMcfgb3+avO67BywEcBNx519qV3zTecvh/nr2YksG8MFBxmI3yj3P\n1HKfMMjPUfUriOM5eEKJcwvJqfrTbACzRjHkiY29gBjA8L5AnGYMwEWN3ha6RJy6\nMAYfNbSwzpGrHPby7I/6Fnee06H3rZ/+xNZfcQzPZCJsUOWbE/mZlAx4Zj3NiIb+\nnUULzIhZIPdBcBs8YW132cpCLzcFFPWRzdhA+bSiQm3G1jcrZY3H8lq6JHas+7bT\nRzXz9FQ7epRCp/MSsbcuya/FUo+CyM9PwX6JKxHw++7EzSTpPN0paLTaA/Iq2SxT\nSQDTvNdpAgMBAAECggEAKtbH9+y1VazrD0WKtYOeeKk2q6qe4oHvqWkax7xNU8Df\nI6D8U3bt273aRgWnV4Is7slox8TWatNCrVgxLJe6mbza8HhtML5NkMTR/cLKOjAO\nsHlUNVdxrMuf2nUyXOw8cRhlbornDFe0so7xRllZy71T87QbJ1ZZoR5pkjsxdUr0\nC9bzcZUcEBBtjaF93JfsF6XAvjSsYH6/ZQduqNuN6BX6dO6ZO9+Cbq8uOR+VXbKq\nogdgGOMXX86t1EbDvB50duv/kdj+dYsyaSKL2laKQr/GLwrBSMFvwEZLs5GxmOwe\nfO7+BDi3nv05LyTDseAJdkGocbWKXMV6bwBAjTgH8QKBgQDZUuBAJxfVvTxbwc4r\nUJr4RsVkRT9pxth7YDszxgjNgJTR0HPaPSDCSEX4QwhbWatZy+bPXFuJlMN53Tpz\njzXfszyMlJhM2eLC3ROSNmaA2tCed9FdEJqSFaKhe2e64vC3PCuW7b0nvPgkdyoO\nMzTKHbtmlmynHck5KJbWy+d1TQKBgQDLKBRXbzUBFOJKMhDxpPJNlaTuLiDsAVrM\nMzr2XHQZJLGInAqr/OXU70voYqrmV8xMXNaheeZUZbuAtMa2Bl0eS02FFkzky7Iv\nip9QcVs9/myld8qVAmjJAzrm8ejcuq1AJRy9BLOxT9oVLwUQGJ7lIy9k4z1HFU4c\nVE+yRXgsjQKBgD2tr8eFUNZwprjEAGd6sQDV1R/oJ181+CrL3QGMquLoI1SI/Nhr\nkOiS6ojTPYPvpxoNLKydYb1iYzgq+XPiqT+b9wtPAQqOrDTx2aQdnGnlsF/JUbpA\nBB6B1W5PP9linz7h7N0hDBZDI4n16BGvpsPWPGGZP60OXxXB102PAVnhAoGAZB91\nnv3MxqKvP9fa5+zeCgSlS0lqqkWkpRzeg0pfYYDnCie1TrwN3VquM3JlPa6pnjzm\n/qAgNxoIRc9SW6VZQTPlmaC69su5HpsYF0I2sJ/ylb4rFjMgx2iTH/y7QgWymvlv\nZ2yozstG9Me+nAc2UEF9+x/PNHg4jdezi22XY4UCgYEAylTRauWSC4wYiwC73NcM\nHeMnvj1wGXhBFRcdyOH1hrCCofkcs7am5OGIwjRTXj2Pe4rCZvLFG2aSWAGzYeL3\nLAC8K+Z1dGI5OcPg8t1sJ+4yqO1IP4452eHlNB5/09Bk/1IU9/64wBTIwxMGW3Z+\nwJzVDKS8gHHgOro7DlC7sSE=\n-----END PRIVATE KEY-----\n",
            "client_email": "sheets@astute-charter-425618-q7.iam.gserviceaccount.com",
            "client_id": "116398454531310558463",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets%40astute-charter-425618-q7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"}
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  
        credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        SPREADSHEET_ID = '1EVJWvK17OUnG4wEd3TuRVhTQTindyEgCsLoOviQjOOY'  # Your Google Sheets ID
        # Convert DataFrame to list of lists
        list_fresh_records = df_fresh_data.values.tolist()
        list_fresh_records
        list_fresh_records.insert(0, df_fresh_data.columns.tolist())
        list_fresh_records
        if list_fresh_records != [[]] : # if the table in not empty 
            if list_fresh_records[1][0] not in {'idealo', 'geizhals','solario24'}:
                fresh_records_after_reformat = Tools.add_past_prices(list_fresh_records,list_old_records)
                fresh_records_after_reformat
                data_after_foramt = Tools.reformat_results_list(original_data= list_old_records,
                                                                list_populated_data= fresh_records_after_reformat)
                                                            
            elif list_fresh_records[1][0] in {'idealo', 'geizhals'} : 
                data_after_foramt = Tools.reformat_results_list_idealo_geizhals(original_data= list_old_records,
                                                                                df_fresh_data = df_fresh_data)
            
            elif list_fresh_records[1][0] == 'solario24' : 
                data_after_foramt = Tools.reformat_results_list_solrio24(df_fresh_data = df_fresh_data ,
                                                                        list_old_records= list_old_records) 
            
            # sorting dataframe columns
            list_list_records = Tools.sorting_dataframe_columns(data_after_foramt)
                        
            
            body = {'values': list_list_records}
            
        else : # this except to handel error if the table is empty 
            if range_table in ['AW9:BB1000','BC9:BH1000'] : 
                body = {'values': [['URL','Name + Preis','Name + Preis','Name + Preis','Name + Preis','Name + Preis']]}
            else : 
                body = {'values': [['URL','Preise','Verfügbar','Bisherige Preise']]}
        
        if range_table == 'B9:B1000' :
            range_table = 'D9:D1000'

        # Write data to the Google Sheets
        results = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!{range_table.split(':')[0]}",   # change download cell 
        valueInputOption='RAW',
        body=body).execute()
        
        
        # UPDATE DATA CELL IN [L6]
        cet_tz = pytz.timezone('CET')
        current_date = datetime.now(cet_tz)
        formatted_date = [[f'aktualisiert : {current_date.strftime("%d.%m.%Y - %H:%M")}']]
        body = {'values': formatted_date}
        service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!L6",   # change download cell 
        valueInputOption='RAW',
        body=body).execute()
    
            
            
        print(f'** {results.get("updatedCells")} cells updated.')
                                    
    @retry_decorator
    def read_google_sheets(range,sheet_name):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        SERVICE_ACCOUNT_FILE = {
            "type": "service_account",
            "project_id": "astute-charter-425618-q7",
            "private_key_id": "f97df6dbdb34806e8c1d73ee6425800be96d50c5",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCsdr4KnB0pYOXp\n9j/tGk8a5uAbMcfgb3+avO67BywEcBNx519qV3zTecvh/nr2YksG8MFBxmI3yj3P\n1HKfMMjPUfUriOM5eEKJcwvJqfrTbACzRjHkiY29gBjA8L5AnGYMwEWN3ha6RJy6\nMAYfNbSwzpGrHPby7I/6Fnee06H3rZ/+xNZfcQzPZCJsUOWbE/mZlAx4Zj3NiIb+\nnUULzIhZIPdBcBs8YW132cpCLzcFFPWRzdhA+bSiQm3G1jcrZY3H8lq6JHas+7bT\nRzXz9FQ7epRCp/MSsbcuya/FUo+CyM9PwX6JKxHw++7EzSTpPN0paLTaA/Iq2SxT\nSQDTvNdpAgMBAAECggEAKtbH9+y1VazrD0WKtYOeeKk2q6qe4oHvqWkax7xNU8Df\nI6D8U3bt273aRgWnV4Is7slox8TWatNCrVgxLJe6mbza8HhtML5NkMTR/cLKOjAO\nsHlUNVdxrMuf2nUyXOw8cRhlbornDFe0so7xRllZy71T87QbJ1ZZoR5pkjsxdUr0\nC9bzcZUcEBBtjaF93JfsF6XAvjSsYH6/ZQduqNuN6BX6dO6ZO9+Cbq8uOR+VXbKq\nogdgGOMXX86t1EbDvB50duv/kdj+dYsyaSKL2laKQr/GLwrBSMFvwEZLs5GxmOwe\nfO7+BDi3nv05LyTDseAJdkGocbWKXMV6bwBAjTgH8QKBgQDZUuBAJxfVvTxbwc4r\nUJr4RsVkRT9pxth7YDszxgjNgJTR0HPaPSDCSEX4QwhbWatZy+bPXFuJlMN53Tpz\njzXfszyMlJhM2eLC3ROSNmaA2tCed9FdEJqSFaKhe2e64vC3PCuW7b0nvPgkdyoO\nMzTKHbtmlmynHck5KJbWy+d1TQKBgQDLKBRXbzUBFOJKMhDxpPJNlaTuLiDsAVrM\nMzr2XHQZJLGInAqr/OXU70voYqrmV8xMXNaheeZUZbuAtMa2Bl0eS02FFkzky7Iv\nip9QcVs9/myld8qVAmjJAzrm8ejcuq1AJRy9BLOxT9oVLwUQGJ7lIy9k4z1HFU4c\nVE+yRXgsjQKBgD2tr8eFUNZwprjEAGd6sQDV1R/oJ181+CrL3QGMquLoI1SI/Nhr\nkOiS6ojTPYPvpxoNLKydYb1iYzgq+XPiqT+b9wtPAQqOrDTx2aQdnGnlsF/JUbpA\nBB6B1W5PP9linz7h7N0hDBZDI4n16BGvpsPWPGGZP60OXxXB102PAVnhAoGAZB91\nnv3MxqKvP9fa5+zeCgSlS0lqqkWkpRzeg0pfYYDnCie1TrwN3VquM3JlPa6pnjzm\n/qAgNxoIRc9SW6VZQTPlmaC69su5HpsYF0I2sJ/ylb4rFjMgx2iTH/y7QgWymvlv\nZ2yozstG9Me+nAc2UEF9+x/PNHg4jdezi22XY4UCgYEAylTRauWSC4wYiwC73NcM\nHeMnvj1wGXhBFRcdyOH1hrCCofkcs7am5OGIwjRTXj2Pe4rCZvLFG2aSWAGzYeL3\nLAC8K+Z1dGI5OcPg8t1sJ+4yqO1IP4452eHlNB5/09Bk/1IU9/64wBTIwxMGW3Z+\nwJzVDKS8gHHgOro7DlC7sSE=\n-----END PRIVATE KEY-----\n",
            "client_email": "sheets@astute-charter-425618-q7.iam.gserviceaccount.com",
            "client_id": "116398454531310558463",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets%40astute-charter-425618-q7.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
            }
        
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
        
        # Authorize the client
        client = gspread.authorize(credentials)
        SPREADSHEET_ID = '1EVJWvK17OUnG4wEd3TuRVhTQTindyEgCsLoOviQjOOY'  # Your Google Sheets ID

        
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name) # or use sheet number
        # Read data from the specified range
        cell_range = sheet.get(range)
        cell_range
        # Convert the cell range to a list of dictionaries, assuming the first row is the header
        headers = cell_range[0]
        data = [dict(zip(headers, row)) for row in cell_range[1:]]
        return data

class Tools : 
    
    def run_with_timeout_chrome_driver(timeout,func,page_link):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func,page_link)
            try:
                driver = future.result(timeout=timeout)
                print('ChromeDriver launched and navigated successfully')
                return driver  # Indicate success
            except concurrent.futures.TimeoutError:
                print("Operation timed out")
                raise TimeoutException("Operation timed out")
            except Exception as e :
                warning_list.append(f'Error : {e} in line 698')
                Tools.sending_email('warning',warning_list)
    
    def sorting_dataframe_columns(listof_lists_records):
        if len(listof_lists_records[0]) == 4 :
            data_after_foramt_dataframe = pd.DataFrame(data = listof_lists_records[1:],columns= listof_lists_records[0])
            data_after_foramt_after_sort_df = data_after_foramt_dataframe[['URL','Preise','Verfügbar','Bisherige Preise']]
            # convert data frame to list of lists 
            body = data_after_foramt_after_sort_df.values.tolist()
            columns = data_after_foramt_after_sort_df.columns.tolist()
            list_list_records = [columns] + body 
            return list_list_records
                
            
        elif len(listof_lists_records[0]) == 6 :
            list_list_records = listof_lists_records
            return list_list_records
        elif len(listof_lists_records[0]) == 1 :
            list_list_records = listof_lists_records
            return list_list_records
        
    def fill_missing_values(list_dicts):
        new_list = []
        for dict in list_dicts:
            if dict == {} : 
                dict['URL'] = '-'
            # if len(dict) == 1 :
            #     if dict['URL'] == None or dict['URL'] == '' : dict['URL'] = '-' 
            # elif len(dict) == 4 :
            #     if dict['URL'] == None or dict['URL'] == '' : dict['URL'] = '-' 
            #     if dict['Preise'] == None or dict['Preise'] == '' : dict['Preise'] = '-' 
            #     if dict['Verfügbar'] == None or dict['Verfügbar'] == '' : dict['Verfügbar'] = '-' 
            #     if dict['Bisherige Preise'] == None or dict['Bisherige Preise'] == '' : dict['Bisherige Preise'] = '-' 
            # elif len(dict) == 6 :  
            #     if dict['URL'] == None or dict['URL'] == '' : dict['URL'] = '-'  
            #     if dict['Name + Preis'] == None or dict['Name + Preis'] == '' : dict['Name + Preis'] = '-'  
                
            new_list.append(dict)
        return new_list
        
    def sending_email(flag, warning_list=[],port = 465):
        # Email details
        smtp_server = 'mail.solario24.com'
        username = 'tectools@solario24.com'
        password = 'RkKz2MzFFQU4v2bfpBJ'
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = username
        # emails_list = ['ramezrasmy876@gmail.com']
        emails_list = ['Roziegert@gmail.com']
        df_warning = '\n'.join(warning_list)
        if flag == 'warning':
            # Body of the email
            msg['Subject'] = 'Warning'
            body = f'Issue Detected with Market_monitor Crawler\n\n - Error: {df_warning} \n - Further Details: Please check the app/logging.txt file inside the container for more information.'
            msg.attach(MIMEText(body, 'plain'))
        elif flag == 'success':
            # Body of the email
            msg['Subject'] = 'Success'
            body = f'The google sheet was updated successfully!'
            msg.attach(MIMEText(body, 'plain'))
        # Send the email
        for email in emails_list:
            msg['To'] = email
            if port == 587 :
                try:
                    with smtplib.SMTP(smtp_server, port) as server:
                        server.ehlo()  # Identify to the server
                        server.starttls()  # Secure the connection using TLS
                        server.ehlo()  # Re-identify to the server after securing the connection
                        server.login(username, password)
                        server.sendmail(msg['From'], msg['To'], msg.as_string())
                        print('\n***\n***\nEmail sent successfully!\n***\n***\n')
                        print(f'\n***\n***\nBody Email : {body}\n***\n***\n')
                except Exception as e:
                    print(f'Error 587 : {e}')
            elif port == 465 :
                try:
                    # Use SMTP_SSL for a secure connection on port 465
                    with smtplib.SMTP_SSL(smtp_server, port) as server:
                        server.login(username, password)  # Login to the email server
                        server.sendmail(msg['From'], msg['To'], msg.as_string())
                        print('\n***\n***\nEmail sent successfully!\n***\n***\n')
                        print(f'\n***\n***\nBody Email: {body}\n***\n***\n')
                except Exception as e:
                    print(f'Error 465: {e}')

    def screenshot(driver,screenshot_name):
        screenshot_path = f'/app/{screenshot_name}.png'
        driver.save_screenshot(screenshot_path)
    
    def print_locale_settings():
        # Get the current locale settings for all categories
        locale_info = locale.localeconv()

        # Print the current locale settings
        print("Locale settings:")
        for key, value in locale_info.items():
            print(f"{key}: {value}")

        # Alternatively, you can print the locale for specific categories
        print("\nSpecific locale settings:")
        print(f"LC_CTYPE: {locale.setlocale(locale.LC_CTYPE)}")
        print(f"LC_NUMERIC: {locale.setlocale(locale.LC_NUMERIC)}")
        print(f"LC_TIME: {locale.setlocale(locale.LC_TIME)}")
        print(f"LC_COLLATE: {locale.setlocale(locale.LC_COLLATE)}")
        print(f"LC_MONETARY: {locale.setlocale(locale.LC_MONETARY)}")
        # print(f"LC_MESSAGES: {locale.setlocale(locale.LC_MESSAGES)}")

    def set_locale():
        try:
            locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
            logging.info("Locale set to de_DE.UTF-8")
        except locale.Error as e:
            warning_list.append(f'Error setting locale: {e} - Line 693')
            logging.error(f"Error setting locale: {e}")
            
    def draw_final():
        counter = 20
        space_counter = 0
        for i in range(20):
            print(' '*(space_counter)+'*'*(counter)+'*'*(counter))
            counter -= 2 
            space_counter += 2
            
    def read_xlsx_file_New_products_spider() -> set:
        # Read csv file 
        print('line 597')
        path = os.path.join(os.getcwd(), "outputs/Temp_URL.xlsx")
        df = pd.read_excel(path)
        set_records = set(df['URL'].to_list())
        return set_records
        
    def read_csv_file_New_products_spider() -> set:
        # Read csv file 
        print('line 710')
        path = os.path.join(os.getcwd(), "outputs/Temp_URL.csv")
        df = pd.read_csv(path)
        set_records = set(df['URL'].to_list())
        return set_records
        
    def current_date_New_products_spider():
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d_%m_%Y")
        return formatted_date
    
    def enter_user_login(driver):
        # User_Name_input_box
        time.sleep(6)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys('rozi@solario24.com')
        # Pass_word_input_box
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'passwort'))).send_keys('cA5fq@bTYSPNk*')
        # press login button
        # time.sleep(10)
        Tools.screenshot(driver,'screeshot_2') # enter password and email address
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'Submit'))).click()
        print('Login krannich successful')
        return driver
    
    def reformat_results_list_solrio24(df_fresh_data,list_old_records):
        df_1 = df_fresh_data
        df_2 = pd.DataFrame(list_old_records)
        merged_df = pd.merge(df_2,df_1,on='URL',how='left').fillna('-')
        values_list = merged_df['Preise'].values.tolist()
        result_list = list(map(lambda x : str(x),values_list))
        formatted_data = [[item] for item in result_list]
        final_format = [['Preise']] + formatted_data
        return final_format

    def format_price(price):
        # Convert the input price to float if it's not already a float
        price_after_clean = price.replace('€','').replace('*','').strip()
        
        if isinstance(price_after_clean, str):
            if price_after_clean[-3] != '.':
                float_price = float(price_after_clean.replace(',','.'))
            else : 
                float_price = float(price_after_clean.replace(',',''))
                
        elif isinstance(price_after_clean, int):
            float_price = float(price_after_clean)
            
        elif isinstance(price_after_clean, float):
            float_price = price_after_clean
        
        # Format the price to two decimal places
        target_price = float(f'{float_price:.2f}')
        
        # Set the locale to German (Germany)
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
        
        # Format the price according to the German locale
        formatted_price = locale.currency(target_price, grouping=True)
        
        return formatted_price
    
    def reformat_results_list(original_data : list[dict] ,list_populated_data : list[list]) -> list[list] :
        '''
        there are empty rows between records so this function for reformat data extracted from spider to include empty rows
        '''
        df_1_dicts_list = original_data
        df_2 = pd.DataFrame(list_populated_data[1:],columns=list_populated_data[0]).fillna('-')
        new_list_dicts_for_df_1 = []
        
        # open database connection for get the last 5 days records 
        connection,cursor = Database_Mangment.openning_connection()
        
        for record in df_1_dicts_list:
            try : 
                if record['URL'] == '':
                    record['URL'] == '-'
                    record['Bisherige Preise'] = '-'
                    record['Preise'] = '-'
                    record['Verfügbar'] = '-'
                    new_list_dicts_for_df_1.append(record)
                elif record['URL'] == '-':
                    record['Bisherige Preise'] = '-'
                    record['Preise'] = '-'
                    record['Verfügbar'] = '-'
                    new_list_dicts_for_df_1.append(record)
                elif record['URL'] != '-' and record['URL'] != '':
                    record['Bisherige Preise'] = Database_Mangment.Extract_last_5_prices_from_database(cursor,record['URL'])
                    record['Preise'] = df_2[df_2['URL'] == record['URL']]['Preise'].to_list()[0]
                    record['Verfügbar'] = df_2[df_2['URL'] == record['URL']]['Verfügbar'].to_list()[0]
                    new_list_dicts_for_df_1.append(record)

                    
                print(f'687-Record after edit last prices :\n{record}')
            except (IndexError,KeyError) as e : 
                print(f'689-Error ----- >>>>>>> {e}')
                warning_list.append(f'Reformat Record {e} , Line 810')
                warning_list.append(f'Link Record {record["URL"]}')
                new_list_dicts_for_df_1.append(record)
        
        merged_df = pd.DataFrame(new_list_dicts_for_df_1).fillna('-')
        print('line 693')
        print(tabulate(merged_df))
        keys_list = merged_df.keys().tolist()
        values_list = merged_df.values.tolist()
        values_list
        # close connection to database
        Database_Mangment.CloseConnection(connection,cursor)
        
        return [keys_list] + values_list

    def reformat_results_list_idealo_geizhals(original_data , df_fresh_data):
        # Rearrange the records to have shop_name with prices in the same cell
        print(f'line 248 original_data : {original_data}')
        print(f'line 249 df_fresh_data : {df_fresh_data}')
        links_list = list(set(df_fresh_data['URL'].to_list()))
        gross_list = []
        gross_list.append(['URL','Name + Preis','Name + Preis','Name + Preis','Name + Preis','Name + Preis'])
        for link in links_list:
            df_first_5_rows = df_fresh_data[df_fresh_data['URL'] == link].head(5)

            link = df_first_5_rows['URL'].to_list()[0]
            Name_shop_list = df_first_5_rows['Name_shop'].to_list()
            Price_list = df_first_5_rows['Preise'].to_list()
            product_list = []
            product_list.append(link)
            for i in range(len(Name_shop_list)):
                product_list.append(Name_shop_list[i] + ' - ' + Price_list[i])
            gross_list.append(product_list)
            
        # merge old records with new records to get the same structure
        df_1 = pd.DataFrame(original_data).fillna('-')
        df_1.columns = df_1.columns.str.strip()
        df_1['Name + Preis']='-'
        df_2 = pd.DataFrame(gross_list[1:],columns=gross_list[0]).fillna('-')
        df_2.columns = df_2.columns.str.strip()
        merged_df = pd.merge(df_1,df_2,on='URL',how='left').fillna('-')
        list_element_for_drop = ['Name + Preis_x']
            
        for drop_column in list_element_for_drop:
            try : merged_df = merged_df.drop(columns=drop_column)
            except KeyError: 
                warning_list.append('Key Error reformat idealo & geizhals - line 855')
                pass 
        merged_df = merged_df.rename(columns={'Name + Preis_y':'Name + Preis'})
        
        keys_list = merged_df.keys().tolist()
        print(f'line 277 {keys_list}')
        values_list = merged_df.values.tolist()
        print(f'line 279 {values_list}')
        return [keys_list] + values_list

    def add_past_prices(list_fresh_records,list_old_records):
        # print(list_fresh_records)
        gross_lists = []
        #['Source', 'URL', 'Produkt', 'Verfügbar', 'Preise', 'Date']
        for record in list_fresh_records:
            new_list = []
            new_list.append(record[1])  # URL
            new_list.append(record[4])  # Price
            new_list.append(record[3])  # Availablility
            gross_lists.append(new_list)   
        gross_lists[0].append('Bisherige Preise')

        print(f'\n\nline 334')
        print(tabulate(gross_lists, headers='keys', tablefmt='pretty'))
        
        df_old_table = pd.DataFrame(list_old_records)
        df_old_table = df_old_table.fillna('-')
        print(f'\n\n line 157 : {pd.DataFrame(df_old_table)}')
        
        for record_list in gross_lists[1:]:
            try : 
                record_list.append('-')
                record_list
            except IndexError : record_list.append('-')
            except KeyError : record_list.append('-')
            except Exception as e :
                print(f'Error {e} , Line 765')
        print(f'\n\n line 161 : {pd.DataFrame(gross_lists)}')
        return gross_lists

    def current_date():
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d.%m.%Y")
        return formatted_date
    
    def delete_old_xlsx_files():
        # Specify the directory
        
        folder_path = os.path.join(os.getcwd(), "outputs")
        # List all files in the directory
        for filename in os.listdir(folder_path):
            if filename.endswith('.xlsx') :
                file_path = os.path.join(folder_path, filename)
                try : os.remove(file_path)
                except Exception as e: 
                    pass
                    print(f'Error line 897 : {e}')
        
    def read_xlsx_file(excel_file):
        # Read csv file 
        path = os.path.join(os.getcwd(), "outputs")
        df = pd.read_excel(path + excel_file)
        df = df.fillna('-')
        # print(df)
        return df


    def last_date(count_days) :
        # Current date
        current_date = datetime.now()
        result_date = current_date - timedelta(days=count_days)
        return result_date.strftime("%d_%m_%Y")

    def different_dates(last_update_record):
        last_update_record = datetime.strptime(last_update_record, "%d.%m.%Y")
        current_date_record = datetime.now()
        difference = current_date_record - last_update_record
        return difference.days

    def current_date_for_database():
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d_%m_%Y")
        return formatted_date
        
    def reformat_data_for_dates(connection,cursor,new_record):
        '''Comparing and reformat new records and old records'''

        try : 
            
            old_record = Database_Mangment.extract_record_from_database_using_url(connection,cursor,'Follow_Up_Competitors_Prices',new_record['URL'])
            # compare the prices and moving old price to another columns and update the 'recent price' column
            new_price = new_record['Preise']
            
            # update database with new column for current date 
            # get current date 
            new_columns_date = Tools.current_date_for_database()
            # add current date as new column

            list_column_date = pd.DataFrame([old_record]).keys().to_list()

            # update column date 
            old_record['Date'] = Tools.current_date_for_database()
            if 'www.idealo' not in old_record['URL'] and 'geizhals' not in old_record['URL']  :
                old_record[new_columns_date] = new_price # record the new price to column current date
                for i in range(1,6): # update the columns with prices 
                    column_date = Tools.last_date(i).replace('.','_')
                    if column_date in list_column_date :
                        old_record[f'Price_{i}_day_ago'] = old_record[column_date]
                    else : 
                        old_record[f'Price_{i}_day_ago'] = None
                
            return old_record
        except ValueError: # for handaling missing records
            # update column date 
            df = pd.DataFrame([new_record])
            df_record_after_edit_columns_headers = df.rename(columns={'Produkt': 'Product_name','Verfügbar':'available', 'Preise': 'Price'}, inplace=False)
            record = df_record_after_edit_columns_headers.to_dict(orient='records')[0]
            today_date = Tools.current_date_for_database()
            today_date
            record['Date'] = today_date
            record[today_date] = record['Price']
            return record
            
                
        


                
                # old_record['Price_today'] = new_price
                
        #     list_dicts_old_records_after_edit = pd.DataFrame([old_record]).to_dict(orient='records')
        # new_list_after_edit_for_database.append(list_dicts_old_records_after_edit)
        # return new_list_after_edit_for_database

class Processing:
    def processing_update_records(list_dicts_new_records):
        connection,cursor = Database_Mangment.openning_connection()
        for record in list_dicts_new_records:

            print(f'Update Record : {record}')
            # [1] Reformat and comapre the old record with new record
            print('[1] Reformat and comapre the old record with new record')
            record_after_reformat = Tools.reformat_data_for_dates(connection,cursor,record)
            
            # [2] UPDATE COLUMNS AND ADD THE NEW COLUMNS (Date columns)
            print('[2] UPDATE COLUMNS AND ADD THE NEW COLUMNS (Date columns)')
            Database_Mangment.update_column_database(connection,cursor)
        
            # [3] serach AND DELETE for record in database USING url OF RECORDS
            print('[3] serach AND DELETE for record in database USING url OF RECORDS')
            Database_Mangment.delete_record_from_database(connection,cursor,record['URL'])
            
            # [4] add new record to database
            print('[4] add new record to database')
            # print(f'list_dicts_records_after_reformat : {record_after_reformat}')
            
            if connection : 
                Database_Mangment.Add_Records_to_Database_Follow_Up_Competitors_Prices(record_after_reformat,connection,cursor)
                # print(f'Record after edit : {record_after_reformat}')
            else : 
                raise ConnectionError('Database connection not established')

        # close connection after update all records 
        Database_Mangment.CloseConnection(connection,cursor)


class CustomSettingsMiddleware:

    def __init__(self, crawler):
        self.crawler = crawler
        self.default_settings = {
            'CONCURRENT_REQUESTS': crawler.settings.getint('CONCURRENT_REQUESTS'),
            'DOWNLOAD_DELAY': crawler.settings.getfloat('DOWNLOAD_DELAY'),
            'USER_AGENT': crawler.settings.get('USER_AGENT'),
        }
        Tools.set_locale()

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('CUSTOM_SETTINGS_ENABLED', True):
            raise NotConfigured
        return cls(crawler)

    def process_request(self, request, spider):
        custom_settings = request.meta.get('custom_settings')
        if custom_settings:
            if 'CONCURRENT_REQUESTS' in custom_settings:
                spider.custom_concurrent_requests = custom_settings['CONCURRENT_REQUESTS']
            if 'DOWNLOAD_DELAY' in custom_settings:
                request.meta['download_delay'] = custom_settings['DOWNLOAD_DELAY']
            if 'USER_AGENT' in custom_settings:
                request.headers['User-Agent'] = custom_settings['USER_AGENT']

    def process_response(self, request, response, spider):
        custom_settings = request.meta.get('custom_settings')
        if custom_settings and 'CONCURRENT_REQUESTS' in custom_settings:
            spider.custom_concurrent_requests = self.default_settings['CONCURRENT_REQUESTS']
        return response

    def process_exception(self, request, exception, spider):
        custom_settings = request.meta.get('custom_settings')
        if custom_settings and 'CONCURRENT_REQUESTS' in custom_settings:
            spider.custom_concurrent_requests = self.default_settings['CONCURRENT_REQUESTS']
        return None

class Spiders:
    class ProductsSpider(scrapy.Spider): # Solarvie - TomCarsHiFi - solardiscount - tepto - solarvic 
        name = "ProductsSpider"
        
        
        
        user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]
        
        
        folder_path = os.path.join(os.getcwd(), "outputs")
        # print(f'Line 831 , {folder_path}')
        custom_settings = {
            "AUTOTHROTTLE_ENABLED" : True,      #Enable AutoThrottle
            "AUTOTHROTTLE_START_DELAY" : 10,     # The initial download delay
            "AUTOTHROTTLE_MAX_DELAY" : 120 ,     # The maximum download delay to be set in case of high latencies
            "AUTOTHROTTLE_TARGET_CONCURRENCY" : 1.0,  # Average number of requests Scrapy should be sending in parallel to each remote server
            'DOWNLOAD_DELAY': 5,   # 1
            'DOWNLOAD_TIMEOUT' : 180 ,
            'ROBOTSTXT_OBEY' : False,
            'LOG_ENABLED' : True,
            'LOG_LEVEL' : 'DEBUG',
            'CONCURRENT_REQUESTS': 7, #1
            'USER_AGENT': random.choice(user_agents),
            'FEEDS': {rf"{folder_path}\Temp_Output.xlsx": {'format': 'xlsx'}},
            'RETRY_ENABLED' : True,
            'RETRY_HTTP_CODES' : [500, 502, 503, 504, 522, 524, 408] ,
            'RETRY_TIMES' : 3 , 
            'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
            'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
            'FEED_URI': rf"{folder_path}\Temp_Output.xlsx",
            'DOWNLOADER_MIDDLEWARES': {'__main__.CustomSettingsMiddleware': 543}}   # test

        def __init__(self,list_links,*args,**kwargs):
            super(Spiders.ProductsSpider,self).__init__(*args,**kwargs)
            self.input_list_links = list_links
            self.output_extracted_records = []

        def start_requests(self) -> EC.Iterable[scrapy.Request]:
            
            print('---------- >>>>>> line 853',self.input_list_links)
            if 'krannich-solar' in self.input_list_links[0] :
                # print('*'*100)
                yield scrapy.Request(url=self.input_list_links[0] ,
                            callback= self.parse_krannich , 
                            meta = {'input_list_links' : self.input_list_links})
         
            elif 'hornbach' in self.input_list_links[0] :
                print('**** --- hornbach')
                yield scrapy.Request(url='https://books.toscrape.com/index.html' , # Dumb link just for running parse function
                    callback= self.parse_hornbach , 
                    meta = {'input_list_links' : self.input_list_links})
                
            elif '.otto.' in self.input_list_links[0] :
                print('**** --- otto')
                yield scrapy.Request(url='https://www.google.com.eg/' , # Dumb link just for running parse function
                    callback= self.parse_otto , 
                    meta = {'input_list_links' : self.input_list_links})
        
            else : 
                for link in self.input_list_links:
                    if 'solarvie' in link :
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_Solarvie_page , errback=self.handle_error, meta = {'url' : link})
                        except Exception as e :
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            warning_list.append(f'This Link is not Valid : {link}')
                            pass
                            
                    elif 'toms-car-hifi' in link :
                        print(f'-- >> Sending requests to : {link}')
                        time.sleep(3)
                        try : yield scrapy.Request(link , callback = self.parse_TomCarsHiFi_page , errback=self.handle_error ,
                            meta={
                                'url' : link,
                                'download_slot': 'custom',  # To isolate from global settings
                                'custom_settings': {
                                    'CONCURRENT_REQUESTS': 1,
                                    'DOWNLOAD_DELAY': 100}})
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                        
                    elif 'solardiscount' in link :
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_solardiscount_page , meta = {'url' : link}, errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                        
                    elif 'tepto' in link :
                        print(f'-- >> Sending requests to : {link}')
                        yield scrapy.Request(link , callback = self.parse_tepto_page , meta = {'url' : link} , errback=self.handle_error)

                        
                    elif 'solarvic' in link :
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_solarvic_page , meta = {'url' : link} , errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                        
                    elif 'idealo' in link :
                        print('line 326 --------------')
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_idealo_page ,  errback=self.handle_error,
                            meta={
                                'url' : link,
                                'download_slot': 'custom',  # To isolate from global settings
                                'custom_settings': {
                                    'CONCURRENT_REQUESTS': 1,
                                    'DOWNLOAD_DELAY': 1,
                                    'USER_AGENT': 'my_custom_user_agent (+http://www.example.com)'}})
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                        
                    elif 'geizhals' in link : 
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_geizhals_page , meta = {'url' : link}, errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                        
                    elif 'solario24' in link : 
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_solario24 , meta = {'url' : link}, errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                
                    elif 'offgridtec' in link : 
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_offgridtec , meta = {'url' : link}, errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                        
                    elif 'enercab' in link :
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_Enercab , meta = {'url' : link}, errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
    
                    elif 'solarspeicher24' in link :  
                        print(f'-- >> Sending requests to : {link}')
                        try : yield scrapy.Request(link , callback = self.parse_solarspeicher24 , meta = {'url' : link}, errback=self.handle_error)
                        except Exception as e :
                            warning_list.append(f'This Link is not Valid : {link}')
                            print(f'Warning {e}')
                            print(f'This Link is not Valid : {link}')
                            pass
                    
        
        
                    
        def check_product_available(response):
            if response.xpath("//*[contains(text(),'http://schema.org/InStock')]|//*[contains(@href,'http://schema.org/InStock')]|//link[@itemprop='availability']/@href|//meta[@content='http://schema.org/InStock']").getall() != [] :
                return 'Ja'
            else : 
                return 'Nein'
            
        def parse_Solarvie_page(self , response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url') 
            try :
                product_dict = {
                        'Source' : 'Solarvie',
                        'URL' : url,
                        'Produkt' : response.xpath('normalize-space(//h1/text())').get().strip(),
                        'Verfügbar' : Spiders.ProductsSpider.check_product_available(response),
                        'Preise' : response.xpath('//*[@id="b-price"]//span[@class="#price-value my-product-price"]/text()').get().replace('€','') + ' €',
                        'Date' : Tools.current_date()}
                yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                product_dict = {
                'Source' : 'Solarvie', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict  
                
            
        def parse_TomCarsHiFi_page(self, response):
            try : 
                print(f"Response status: {response.status}")
                url = response.meta.get('url')
                product_dict = {
                        'Source' : 'Tom_Cars_Hi_Fi', 
                        'URL' : url,
                        'Produkt' : response.xpath('//meta[@property="og:title"]/@content').get(),
                        'Verfügbar' : Spiders.ProductsSpider.check_product_available(response),
                        'Preise' : Tools.format_price(response.xpath('//meta[@property="product:price"]/@content').get()),
                        'Date' : Tools.current_date()}
                yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                product_dict = {
                'Source' : 'Tom_Cars_Hi_Fi', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict  
                
                
        def parse_solardiscount_page(self, response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            try : 
                product_dict = {
                        'Source' : 'SolarDiscount', 
                        'URL' : url,
                        'Produkt' : response.xpath('//meta[@property="og:title"]/@content').get(),
                        'Verfügbar' : Spiders.ProductsSpider.check_product_available(response),
                        'Preise' : response.xpath('//meta[@property="og:price:amount"]/@content').get() + ' €',
                        'Date' : Tools.current_date()}
                yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}')
                product_dict = {
                'Source' : 'SolarDiscount', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict  

        def parse_tepto_page(self, response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            try : 
                product_dict = {
                        'Source' : 'Tepto', 
                        'URL' : url,
                        'Produkt' : response.xpath('//meta[@property="og:title"]/@content').get(),
                        'Verfügbar' : Spiders.ProductsSpider.check_product_available(response),
                        'Preise' : response.xpath('//p[@class="product-detail-price"]/text()|//p[@class="product-detail-price with-list-price"]/text()').get().strip().replace('\xa0','').replace('*','').replace('€',' €'),
                        'Date' : Tools.current_date()}
                yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                product_dict = {
                'Source' : 'Tepto', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict 


        def parse_solarvic_page(self, response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            try : 
                product_dict = {
                        'Source' : 'Solarvic', 
                        'URL' : url,
                        'Produkt' : response.xpath('//meta[@property="og:title"]/@content').get(),
                        'Verfügbar' : Spiders.ProductsSpider.check_product_available(response),
                        'Preise' : Tools.format_price(response.xpath('//meta[@itemprop="price"]/@content').get()),
                        'Date' : Tools.current_date()}
                yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}')
                product_dict = {
                'Source' : 'Solarvic', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict 
                

        def parse_krannich(self,response):
            
            print('line 368'*100)
            input_list_links = response.meta.get('input_list_links')
            print('Enter krannich customer login page [1]')
            
            # while loop for if the driver is not running and timeout 
            retry_time = 0
            max_retries = 4
            timeout = 60  # seconds
            while retry_time < max_retries:
                try:
                    retry_time += 1
                    print(f"Attempt {retry_time} of {max_retries}")
                    driver = Tools.run_with_timeout_chrome_driver(timeout,BrowserHandler.launch_driver,'https://shop.krannich-solar.com/customerlogin')
                    if driver:
                        break  # Exit the loop if the function succeeds
                except TimeoutException:
                    print(f"Retrying... (attempt {retry_time})")
                    continue
                
                except Exception as e:
                    print(f'>>>>>>> Error : {e} line 1517')
                        
            
            
            # driver = BrowserHandler.launch_driver('https://shop.krannich-solar.com/customerlogin')
            print('Enter krannich customer login page [2]')
            # press Cockes_button
            # time.sleep(10)
            Tools.screenshot(driver,'screenshot_1')
            try :WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'))).click()
            except TimeoutException : pass 
            print('Enter krannich customer login page [3]')
            driver = Tools.enter_user_login(driver)
            print('Enter krannich customer login page [4]')
            for link in input_list_links:
                
                try : 
                    driver.get(link)    
                    print(f'-- >> Sending requests to : {link} ')
                    print('** Loading product page [1]')
                    try : 
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//h2')))
                        product_name_list = driver.find_elements(By.XPATH, '//h2')
                        if len(product_name_list) > 1 :
                            product_name = product_name_list[1].text.strip()
                        elif len(product_name_list) == 1 :
                            product_name = product_name_list[0].text.strip()
                            
                    except Exception as e  : 
                        print(f'Error in porducts names line : 1547 {e}')
                        product_name = '-'
                    print('** Loading product page [2]')
                    try : 
                        product_price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="price--default is--nowrap"]'))).text.replace('*','')
                    except (TimeoutException,NoSuchElementException,StaleElementReferenceException) as e:
                        print(f'---------- >>>>>>>>>> Error is line 1075 {e}')
                        product_price = '-'
                        Google_sheets.Add_one_Record_to_Database_New_products_spider(SOURCE = 'krannich' , URL = link)
                        continue

                    print('** Loading product page [3]')
                    try : 
                        availabel_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'http://schema.org/InStock')]|//*[contains(@href,'http://schema.org/InStock')]|//link[@itemprop='availability']"))).text.strip()
                        if availabel_element != []: 
                            product_availability =  'Ja'
                        else : 
                            product_availability = 'Nein'
                    except (TimeoutException,NoSuchElementException,StaleElementReferenceException) as e: 
                        print(f'---------- >>>>>>>>>> Error is line 1098 {e}')
                        product_availability = '-'
                    print('** Loading product page [4]')
            
                    product_dict = {
                            'Source' : 'Krannich', 
                            'URL' : link,
                            'Produkt' : product_name ,
                            'Verfügbar' : product_availability ,
                            'Preise' : product_price,
                            'Date' : Tools.current_date()}
                    print(f'Record : {product_dict}')
                    print(f'Response status: 200')
                    yield product_dict
                    
                except Exception as e :
                    print(f'Warning {e}')
                    print(f'This Link is not Valid : {link}')
                    warning_list.append(f'This Link is not Valid : {link}')
                    Database_Mangment.Add_unvalid_url_to_Database_New_products(url = link,source = 'krannich')
                    continue
            if warning_list != [] : 
                Tools.sending_email('warning', warning_list)
                
            driver.close()


        def parse_otto(self,response):
            print('*+-'*5)
            input_list_links = response.meta.get('input_list_links')
            print('*-'*20,input_list_links)
            print(' [1] Enter Otto Product pages')
            # while loop for if the driver is not running and timeout 
            retry_time = 0
            max_retries = 4
            timeout = 60  # seconds
            while retry_time < max_retries:
                try:
                    retry_time += 1
                    print(f"Attempt {retry_time} of {max_retries}")
                    driver = Tools.run_with_timeout_chrome_driver(timeout,BrowserHandler.launch_driver,'https://books.toscrape.com/')
                    if driver:
                        break  # Exit the loop if the function succeeds
                except TimeoutException:
                    print(f"Retrying... (attempt {retry_time})")
                    continue
                
                except Exception as e:
                    print(f'>>>>>>> Error : {e} line 1517')

            print('[2] Enter Otto Product pages')
            Tools.screenshot(driver,'screenshot_10')

            for link in input_list_links :
                try :
                    driver.get(link)
                    # [1] Extract Product name 
                    try :Produkt = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pdp_short-info__main-name js_pdp_short-info__main-name pl_headline100 pl_headline200--lg"]'))).text
                    except TimeoutException : Produkt = '-'
                    # [2] Extract is this product is avaulable 
                    try :
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'https://schema.org/InStock')]"))).text
                        avialbel = 'Ja'
                    except : 
                        avialbel = 'Nein' 
                    # [3] Extract is this Products Price 
                    try :Preise = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//span[@class="js_pdp_price__retail-price__value_ pl_headline300"]'))).text.replace('\xa0',' ')
                    except TimeoutException : Preise = '-'
                    product_dict = {
                        'Source' : 'Otto', 
                        'URL' : link,
                        'Produkt' : Produkt ,
                        'Verfügbar' : avialbel ,
                        'Preise' : Preise,
                        'Date' : Tools.current_date()}
                    yield product_dict
                except Exception as e :
                        print(f'Warning {e}')
                        print(f'This Link is not Valid : {link}')
                        warning_list.append(f'This Link is not Valid : {link}')
                        continue
            if warning_list != [] : 
                Tools.sending_email('warning', warning_list)
            driver.close()




        def parse_hornbach(self,response):
            print('*****------ parser')
            input_list_links = response.meta.get('input_list_links')
            print('Enter Hornbach Products page')
            
            
            
            # while loop for if the driver is not running and timeout 
            retry_time = 0
            max_retries = 4
            timeout = 60  # seconds
            while retry_time < max_retries:
                try:
                    retry_time += 1
                    print(f"Attempt {retry_time} of {max_retries}")
                    driver = Tools.run_with_timeout_chrome_driver(timeout,BrowserHandler.launch_driver,'https://www.hornbach.de/')
                    if driver:
                        break  # Exit the loop if the function succeeds
                except TimeoutException:
                    print(f"Retrying... (attempt {retry_time})")
                    continue
                
                except Exception as e:
                    print(f'>>>>>>> Error : {e} line 1517')
                        
            
            for link in input_list_links:
                try : 
                    driver.get(link)
                    print('2')

                    
                    try : 
                        driver.find_element(By.XPATH,'//script[contains(text(),"https://schema.org/InStock")]')
                        availabel = 'Ja'
                    except : 
                        availabel = 'Nein'

                    try : name = driver.find_element(By.XPATH,'//h1').text
                    except : name = '-'

                    try : price = driver.find_element(By.XPATH,'//span[@class="zoakp70 zoakp78 m1jmqi1 jkwwka0 fegjvn1 fegjvn0 fegjvn7 fegjvn3"]|//span[@class="zeyhh00 zeyhh08 wmcshs1 _5ibtun0 _1r7wofw1 _1r7wofw0 _1r7wofw7 _1r7wofw3"]').text.replace('*','')
                    except : price = '-'

                    product_dict = {
                            'Source' : 'hornbach', 
                            'URL' : link,
                            'Produkt' : name,
                            'Verfügbar' : availabel,
                            'Preise' : price,
                            'Date' : Tools.current_date()}
                    
                    print(f'Record : {product_dict}')
                    print(f'Response status: 200')
                    yield product_dict
                    
                except Exception as e :
                    print(f'Warning {e}')
                    print(f'This Link is not Valid : {link}')
                    warning_list.append(f'This Link is not Valid : {link}')
                    continue
            
            if warning_list != [] : 
                Tools.sending_email('warning', warning_list)
            
            driver.close()
                
            

        def parse_idealo_page(self, response):  # remining ( geizhals - idealo - krannich)
            # print('454*'*100)
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            try : 
                products_boxes = response.xpath("//li[contains(@class, 'productOffers-listItem row row-24 product-offers-items-soop')]")
                for box in products_boxes:
                    product_dict = {
                        'Source' : 'idealo', 
                        'Produkt' : response.xpath('//h1[@id="oopStage-title"]/span/text()').get(),
                        'URL' : url,
                        'Name_shop' : box.xpath('normalize-space(.//a[@class="productOffers-listItemOfferCtaLeadout button button--leadout"]/@data-shop-name)').get(),
                        'Preise' : box.xpath('normalize-space(.//a[@class="productOffers-listItemOfferPrice"]/text())').get().replace('\xa0',''),
                        'Date' : Tools.current_date()}
                    # print(product_dict)
                    yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}')  
                product_dict = {
                'Source' : 'idealo', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict
                
        def parse_geizhals_page(self,response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            try : 
                products_boxes = response.xpath("//div[contains(@class, 'offer offer--')]")
                for box in products_boxes:
                    product_dict = {
                        'Source' : 'geizhals', 
                        'Produkt' : response.xpath('//h1/text()').get(),
                        'URL' : url,
                        'Name_shop' : box.xpath('normalize-space(.//div[@class="merchant__logo-caption"]/text())').get(),
                        'Preise' : Tools.format_price(box.xpath('normalize-space(.//span[@class="gh_price"]/text())').get().replace('\xa0','')),
                        'Date' : Tools.current_date()}
                    yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                product_dict = {
                'Source' : 'geizhals', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict
    
                
        def parse_offgridtec(self,response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            
        
            if response.xpath('//div[@class="product-detail-delivery-information"]//link/@href').get() == 'http://schema.org/InStock':
                available = 'Ja'
            else : 
                available = 'Nein'
                
            try : name = response.xpath('//h1/text()').get().strip()
            except Exception as e : 
                print(f'-->> line 1454 - Error Type : {e}')
                name = '-'
            
            try : price = response.xpath('//p[@class="product-detail-price"]/text()|//p[@class="product-detail-price"]/text()|//p[@class="product-detail-price with-list-price"]/text()').get().strip().replace('\xa0','').replace('*','').replace('€',' €')
            except Exception as e : 
                print(f'-->> line 1461 - Error Type : {e}')
                price = '-'
            
            product_dict = {
            'Source' : 'offgridtec', 
            'URL' : url,
            'Produkt' : name,
            'Verfügbar' : available , 
            'Preise' : price,
            'Date' : Tools.current_date()}
            product_dict
            yield product_dict
                
        def parse_solario24(self,response):
            print(f"Response status: {response.status}")
            url = response.meta.get('url')
            try : 
                product_prices = response.xpath('//div[@class="product-price"]//bdi/text()').getall()
                if len(product_prices) == 1 : price = product_prices[0]
                elif len(product_prices) == 2 : price = product_prices[1]
                product_dict = {
                'Source' : 'solario24', 
                'Produkt' : response.xpath('//h3[@class="product_title entry-title"]/text()|//h1[@class="product_title entry-title"]/text()').get(),
                'URL' : url , 
                'Preise' : price,
                'Date' : Tools.current_date()}
                yield product_dict
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                product_dict = {
                'Source' : 'solario24', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict
    
        def parse_Enercab(self, response):
            try : 
                print('\n\n')
                print(f"Response status: {response.status}")
                url = response.meta.get('url')
                data_string = response.xpath('//script[@type="application/ld+json"][4]/text()').get()
                if 'https://schema.org/InStock' in data_string : avialbel = 'Ja'
                else : avialbel = 'Nein' 
                
                
                try : price = response.xpath('//span[@class="current-price-value"]/text()').get().strip().replace('\xa0',' ')
                except : price = response.xpath('//span[@class="current-price-value"]/text()').get().replace('\xa0',' ')
                
                
                product_dict = {
                        'Source' : 'Enercab', 
                        'URL' : url,
                        'Produkt' : response.xpath('//title/text()').get(),
                        'Verfügbar' : avialbel,
                        'Preise' : price,
                        'Date' : Tools.current_date()}
                print('\n\nproduct_dict\n\n')
                print(product_dict)
                print('\n\n')
                yield product_dict
            
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                
                product_dict = {
                'Source' : 'Enercab', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict  
                
        def parse_solarspeicher24(self , response):
            try : 
                print('\n\n')
                print(f"Response status: {response.status}")
                url = response.meta.get('url')
                product_dict = {
                        'Source' : 'solarspeicher24', 
                        'URL' : url,
                        'Produkt' : response.xpath('//h1/text()').get().strip(),
                        'Verfügbar' : Spiders.ProductsSpider.check_product_available(response),
                        'Preise' : response.xpath('//span[@id="snippetPriceContainer"]/text()|//span[@class="main-product-price"]/text()').get().strip().replace('\xa0',' ').replace('*',''),
                        'Date' : Tools.current_date()}
                print('\n\nproduct_dict\n\n')
                print(product_dict)
                print('\n\n')
                yield product_dict
            
            except Exception as e:
                print('-->> WARNING <<--') 
                print('-->> Error Parse Product Page <<--')
                print(f'-->> Error Type : {e}') 
                
                product_dict = {
                'Source' : 'solarspeicher24', 
                'URL' : url,
                'Produkt' : '-',
                'Verfügbar' : 'Nein' , 
                'Preise' : '-',
                'Date' : Tools.current_date()}
                product_dict
                yield product_dict  
            
        def handle_error(self,failure):
            
            # Extract the URL that caused the error
            error_link = failure.request.meta['url']
            warning_list = [f'Error link: {error_link}']
            # sending email for unalid email 
            Tools.sending_email('warning',warning_list)
            print('*'*100)
            # Print or log the failed URL
            print(f'Failed to process: {error_link}')

            


    class NewproductsSpider(scrapy.Spider):
        name = "New_products"
        
        
        def __init__(self, *args, **kwargs):
            self.out_out_links = []
        
        user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
        
        # Ensure the output directory exists
        folder_path = os.path.join(os.getcwd(), "outputs")
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, "Temp_URL.csv")

        
        custom_settings = {
            "AUTOTHROTTLE_ENABLED" : True,      #Enable AutoThrottle
            "AUTOTHROTTLE_START_DELAY" : 10,     # The initial download delay
            "AUTOTHROTTLE_MAX_DELAY" : 120 ,     # The maximum download delay to be set in case of high latencies
            "AUTOTHROTTLE_TARGET_CONCURRENCY" : 1.0,  # Average number of requests Scrapy should be sending in parallel to each remote server
            'DOWNLOAD_DELAY': 5,   # 1
            'DOWNLOAD_TIMEOUT' : 180 ,
            'LOG_LEVEL' : 'DEBUG',
            'ROBOTSTXT_OBEY' : False,
            'USER_AGENT': random.choice(user_agents),
            'REQUEST_FINGERPRINTER_IMPLEMENTATION' : '2.7',
            'FEEDS' : {
                file_path: {
                    'format': 'csv',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'fields': None,
                    'indent': 4
                },
            }}
        
        def start_requests(self) :
            data_dict = {
                "parse_tom_cars_newlinks": "https://www.toms-car-hifi.de/web/sitemap/shop-1/sitemap-1.xml.gz",
                "parse_solarvie_newlinks": "https://www.solarvie.at/sitemap_products_1.xml?from=6771157401935&to=9426212421967",
                "parse_solairdicount_newlinks": "https://solardiscount.at/sitemap_products_1.xml?from=8054266364168&to=9322516054280",
                "parse_tepto_newlinks": "https://www.tepto.de/sitemap/salesChannel-afd74fc31aa542a3a496bdfeb8e31f49-2fbb5fe2e29a4d70aa5854ce7ce3e20b/afd74fc31aa542a3a496bdfeb8e31f49-sitemap-www-tepto-de-1.xml.gz",
                "parse_solarvic_newlinks":"https://solarvic.at/export/sitemap_0.xml.gz",
                "parse_offgridtec_newlinks":"https://www.offgridtec.com/sitemap/salesChannel-595e7e3cd1054a66bcae5329477ce637-2fbb5fe2e29a4d70aa5854ce7ce3e20b/595e7e3cd1054a66bcae5329477ce637-sitemap-www-offgridtec-com-1.xml.gz",
                "parse_krannich_newlinks":"https://shop.krannich-solar.com/web/sitemap/shop-1/sitemap-1.xml.gz",
                "parse_enercab_newlinks":"https://www.enercab.at/1_de_0_sitemap.xml",
                "parse_hornbach_newlinks":"https://books.toscrape.com/", 
                "parse_otto_newlinks" : "https://www.google.com/webhp",
                "parse_solarspeicher24_newlinks":"https://solarspeicher24.de/0030e4abe1be4cd1ae7a2b25d98d7ca5-sitemap-solarspeicher24-de-1.xml.gz"
                }
            # data_dict = {"parse_hornbach_newlinks":"https://books.toscrape.com/"}
            
            for key,value in data_dict.items():
                user_agent = random.choice(Spiders.NewproductsSpider.user_agents)
                yield scrapy.Request(
                    url=value,
                    callback=getattr(self,key),
                    headers={'User-Agent': user_agent}
                )

        def parse_enercab_newlinks(self,response):
            print('parse_enercab_newlinks')
            URL_list = response.xpath('//*[(contains(text(),"https://www.enercab.at/")) and contains(text(),".html")]/text()').getall()
            for URL in URL_list:
                record = {
                    'SOURCE' : 'enercab',
                    'URL' : URL,
                    'Update_date' : Tools.current_date()
                }
                yield record

        def parse_tom_cars_newlinks(self, response):
            print('parse_tom_cars_newlinks')
            compressed_file = io.BytesIO(response.body)
            with gzip.GzipFile(fileobj=compressed_file) as f:
                xml_content = f.read()
            response = scrapy.Selector(text=xml_content.decode('utf-8'))
            links_list = response.xpath('//*[contains(text(),"https://www.toms-car-hifi.de/technikwelt/freizeit/solar/")]//text()').getall()
    
            for url in links_list: # control count of links 
                record = {
                    'SOURCE' : 'toms_car_hifi',
                    'URL' : url,
                    'Update_date' : Tools.current_date()}
                yield record
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')
                    
        def parse_solarvie_newlinks(self, response): # ok
            print('parse_solarvie_newlinks')
            URL_list = response.xpath('//*[contains(text(),"https://www.solarvie.at/")]/text()').getall()
    
            for URL in URL_list:
                record = {
                    'SOURCE' : 'solarvie',
                    'URL' : URL,
                    'Update_date' : Tools.current_date()
                }
                yield record
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')
                
        def parse_solairdicount_newlinks(self, response):
            print('parse_solairdicount_newlinks')
            links_list = response.xpath('//*[contains(text(),"https://solardiscount.")]//text()').getall()
            for url in links_list: # control count of links 
                record = {
                    'SOURCE' : 'solardiscount',
                    'URL' : url,
                    'Update_date' : Tools.current_date()}
                yield record
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')
                
        def parse_tepto_newlinks(self,response):
            print('parse_tepto_newlinks')
            compressed_file = io.BytesIO(response.body)
            with gzip.GzipFile(fileobj=compressed_file) as f:
                xml_content = f.read()
            response = scrapy.Selector(text=xml_content.decode('utf-8'))
            links_list = response.xpath('//*[contains(text(),"https://www.tepto")]//text()').getall()
            for url in links_list: # control count of links 
                record = {
                    'SOURCE' : 'tepto',
                    'URL' : url,
                    'Update_date' : Tools.current_date() }
                yield record
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')

        def parse_solarvic_newlinks(self,response):
            print('parse_solarvic_newlinks')
            compressed_file = io.BytesIO(response.body)
            with gzip.GzipFile(fileobj=compressed_file) as f:
                xml_content = f.read()
            response = scrapy.Selector(text=xml_content.decode('utf-8'))
            links_list = response.xpath('//*[contains(text(),"https://solarvic.at/") and not (contains(text(),".jpg"))]//text()').getall()
            for url in links_list: # control count of links 
                record = {
                    'SOURCE' : 'solarvic',
                    'URL' : url ,
                    'Update_date' : Tools.current_date() }
                yield record
                
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')
            
        def parse_offgridtec_newlinks(self,response):
            print('parse_offgridtec_newlinks')
            compressed_file = io.BytesIO(response.body)
            with gzip.GzipFile(fileobj=compressed_file) as f:
                xml_content = f.read()
            response = scrapy.Selector(text=xml_content.decode('utf-8'))
            links_list = response.xpath('//*[contains(text(),"https://www.offgridtec.")]//text()').getall()
            for url in links_list: # control count of links 
                record = {
                    'SOURCE' : 'offgridtec',
                    'URL' : url , 
                    'Update_date' : Tools.current_date() }
                yield record
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')
                

            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products') -------------------------??? 

        def parse_krannich_newlinks(self,response):
            print('parse_krannich_newlinks')
            compressed_file = io.BytesIO(response.body)
            with gzip.GzipFile(fileobj=compressed_file) as f:
                xml_content = f.read()
            response = scrapy.Selector(text=xml_content.decode('utf-8'))
            links_list = response.xpath('//*[contains(text(),"https://shop.krannich-solar.com")]//text()').getall()
            for url in links_list: # control count of links 
                record = {
                    'SOURCE' : 'krannich',
                    'URL' : url , 
                    'Update_date' : Tools.current_date() }
                yield record
                # self.out_out_links.append(record)
            #     list_url.append(record)
            # Database_Mangment.Add_URL_to_Database(list_url,'New_Products')
        
        def parse_hornbach_newlinks(self,response):
            print(response)
            print('parse_hornbach_newlinks')
            link = 'https://www.hornbach.ch/de/c/solar-photovoltaikanlagen/S31735/'
            driver = BrowserHandler.launch_driver(link)
            time.sleep(5)
            all_products = driver.find_elements(By.XPATH,'//div[@data-testid="article-card"]//a')
            all_links = [card.get_attribute('href') for card in all_products]
            for URL in all_links:
                record = {
                    'SOURCE' : 'hornbach',
                    'URL' : URL,
                    'Update_date' : Tools.current_date()
                }
                print(record)
                yield record
            driver.close()
            
            
        def parse_otto_newlinks(self,response):
            print(response)
            print('parse_OTTO_newlinks')
            link = 'https://www.otto.de/baumarkt/solartechnik/solaranlagen/'
            driver = BrowserHandler.launch_driver(link)
            time.sleep(5)
            count_products = 0
            gross_links = []
            for _ in range(10):
                driver.get(f'https://www.otto.de/baumarkt/solartechnik/solaranlagen/?l=gq&o={count_products}')
                count_products += 120
                begain = 0
                end = 2500
                page_count = 1
                # scrolling down the page 
                for _ in range(10):
                    driver.execute_script(f"window.scrollTo({begain}, {end});")
                    begain += 2500
                    end += 2500
                    time.sleep(2)
                    print(f'scrolling down the OTTO page count {page_count}')
                    page_count += 1 
                links_list = driver.find_elements(By.XPATH,'//article[@data-product-listing-type="ProductList"]//a[@class="find_tile__productLink"]')
                gross_links += [link.get_attribute('href') for link in links_list]
            for URL in gross_links:
                record = {
                    'SOURCE' : 'otto',
                    'URL' : URL,
                    'Update_date' : Tools.current_date()
                }
                print(record)
                yield record
            driver.close()
                        
        def parse_solarspeicher24_newlinks(self,response):
            print('parse_solarspeicher24_newlinks')
            compressed_file = io.BytesIO(response.body)
            with gzip.GzipFile(fileobj=compressed_file) as f:
                xml_content = f.read()
            response = scrapy.Selector(text=xml_content.decode('utf-8'))
            links_list = response.xpath('//*[contains(text(),"https://solarspeicher24")]//text()').getall()
            for URL in links_list:
                record = {
                    'SOURCE' : 'solarspeicher24',
                    'URL' : URL,
                    'Update_date' : Tools.current_date_New_products_spider()}
                yield record
                
@defer.inlineCallbacks
def Main():

    # Configure logging
    logging.basicConfig(
        filename='Logging.txt',  # Name of the file to save logs
        level=logging.DEBUG,  # Set the logging level
        format='%(asctime)s - %(lineno)d - %(funcName)s - %(message)s'
    )
    # Tools.set_locale()
    # print('\n************\n')
    # Tools.print_locale_settings()

    # all sheet 
    ranges_list = ['B9:B1000',  
                   'E9:H1000',  
                   'I9:L1000',  
                   'M9:P1000',  
                   'Q9:T1000',  
                   'U9:X1000',  
                   'Y9:AB1000', 
                   'AC9:AF1000', 
                   'AG9:AJ1000', 
                   'AK9:AN1000',
                   'AO9:AR1000',
                   'AS9:AV1000',
                   'AW9:BB1000',
                   'BC9:BH1000'] 
    
    

    sheet_list = ['Solarmodule',
                  'Wechselrichter ',
                  'Speicher',
                  'Wallbox ',
                  'Komplettanlagen',
                  'Platzhalter',
                  'Montagematerial',
                  'Platzhalter2',
                  'Platzhalter3']
    
    
    # Testing Ranges
    # ranges_list = ['B9:B1000']
    # sheet_list = ['Platzhalter3']
    
    
    runner  = CrawlerRunner()
    for sheet_name in sheet_list:
        for range in ranges_list:            
            print(f'-- >> Reading Google Sheets Range : {range} , Sheet Name : {sheet_name}')
            past_table_before_filling_gaps = Google_sheets.read_google_sheets(range,sheet_name)
            past_table = Tools.fill_missing_values(past_table_before_filling_gaps)
            past_table
            df_past_table = pd.DataFrame(past_table)
            if set(df_past_table['URL']) != {'-'}:
                products_list_links = [record['URL'] for record in past_table if record != {} and record['URL'] != '' and record['URL'] != '-']
                if len(products_list_links)>0 : print(f'-- >> Successfully ! Reading Google Sheets , Count of Urls For Extract Data : {len(products_list_links)}')
                else : print('Not Found Urls For Extract Data')
                
                print(f'-- >> list of Target Products :: {products_list_links}')
                # Delete Old xlsx files
                print('-- >> Delete Old xlsx files')
                Tools.delete_old_xlsx_files()
                
                # # Run Crawler Spider
                
                yield runner.crawl(Spiders.ProductsSpider,list_links = products_list_links)
                

                # Read output excel file 
                fresh_table_df = Tools.read_xlsx_file('\Temp_Output.xlsx')
                list_dicts_new_records = fresh_table_df.to_dict(orient='records')
                
                # # # # Update Database following prices table
                print('-- >> Update Database following NEW prices table')
                try : 
                    if list_dicts_new_records[0]['Source'] != 'geizhals' and list_dicts_new_records[0]['Source'] != 'idealo':  
                        Processing.processing_update_records(list_dicts_new_records)
                except :
                    pass
        
                # # Writing data to google sheet file 
                print('-- >> Updating Google Sheet with New Prices ')
                Google_sheets.write_data_to_google_sheets(df_fresh_data = fresh_table_df ,
                                                    range_table = range,
                                                    list_old_records = past_table,
                                                    sheet_name = sheet_name) 
            else : # if empty record
                pass 

    # Delete existing excel files 
    Tools.delete_old_xlsx_files()
    
    # Run crawler to get new records and store in excel file 
    print('-->>  Running New Products Spider')
    
    yield runner.crawl(Spiders.NewproductsSpider)
    
    print('-->>  Finishing New Products Spider Crawling')
    
    # Read excel file and store URLS in List varaiable
    print('-->>  Read excel file and store URLS in List varaiable')
    SET_records_extract_records = Tools.read_csv_file_New_products_spider()
    SET_records_extract_records
    # Read the records from database and save in list of records 
    print('-->>  Read the records from database and save in list of records')
    SET_list_database_urls = set(Database_Mangment.read_records_NEW_PRODUCTS_database_New_products_spider())
    
    print('-->>  Comparing Records from extraction with Records from database')
    # Comparing Records from extraction with Records from database
    list_new_products_links = list(SET_records_extract_records.difference(SET_list_database_urls))
    print('line 1905')
    print(list_new_products_links)
    # Because krannich,Hornbach and Otto websites need selenuim for parse driver and extract data so we need to sperate the url list  
    # [1] List_without_krannich , Hornbach and otto
    # [2] List_with_krannich
    # [3] List_with_Hornbach
    # [4] List_with_Otto
    
    List_without_krannich_Hornbach_otto = [url for url in list_new_products_links if 'shop.krannich' not in url and 'hornbach' not in url and '.otto.' not in url]
    List_without_krannich_Hornbach_otto
    List_with_krannich = [url for url in list_new_products_links if 'shop.krannich' in url]
    List_with_krannich
    List_with_hornbach = [url for url in list_new_products_links if 'hornbach' in url]
    List_with_hornbach
    List_with_otto = [url for url in list_new_products_links if '.otto.' in url]
    List_with_otto
    ''' [1] --- >>> List without krannich , Hornbach and Otto '''
    # Delete existing excel files 
    print('-->>  Delete existing excel files [without_krannich]')
    Tools.delete_old_xlsx_files() 
    
    # Run crawler for get all new products details [products without krannich hornbach and otto]
    print('-->>  Running New ProductsSpider for getting all products details about new products [without_krannich]')
    yield runner.crawl(Spiders.ProductsSpider,list_links = List_without_krannich_Hornbach_otto) #
    
    # Read Excel file extracted new products data [products without krannich hornbach and otto]
    print('-->>  Read Excelf ile extracted new products data [without_krannich]')
    df_new_products_without_krannich = Tools.read_xlsx_file('\Temp_Output.xlsx')
    print('--- >>>Table of New Products without krannich')
    print(tabulate(df_new_products_without_krannich, headers='keys', tablefmt='pretty'))
    new_products_list_dicts_without_krannich = df_new_products_without_krannich.to_dict(orient='records')

    # store new products links to database 
    print('store new products links to database [without_krannich]')
    Database_Mangment.Add_Records_to_Database_New_products_spider(new_products_list_dicts_without_krannich)
    
    ''' [2] --- >>> List_with_krannich '''
    # Delete existing excel files 
    print('-->>  Delete existing excel files [with_krannich]')
    Tools.delete_old_xlsx_files() 
    
    # Run crawler for get all new products details
    print('-->>  Running New ProductsSpider for getting all details about new products [with_krannich]')
    yield runner.crawl(Spiders.ProductsSpider,list_links = List_with_krannich) #
    
    # Read Excelfile extracted new products data 
    print('-->>  Read Excelfile extracted new products data [with_krannich]')
    df_new_products_with_krannich = Tools.read_xlsx_file('\Temp_Output.xlsx')
    print('--- >>>Table of New Products with krannich')
    print(tabulate(df_new_products_with_krannich, headers='keys', tablefmt='pretty'))
    new_products_list_dicts_with_krannich = df_new_products_with_krannich.to_dict(orient='records')
    new_products_list_dicts_with_krannich
    # store new products links to database 
    print('store new products links to database [with_krannich]')
    # LINE 1429
    Database_Mangment.Add_Records_to_Database_New_products_spider(new_products_list_dicts_with_krannich)
    
    
    ###################################################
    ''' [2] --- >>> List_with_Hornbach '''
    # Delete existing excel files 
    print('-->>  Delete existing excel files [with_Hornbach]')
    Tools.delete_old_xlsx_files() 
    
    # Run crawler for get all new products details
    print('-->>  Running New ProductsSpider for getting all details about new products [with_Hornbach]')
    yield runner.crawl(Spiders.ProductsSpider,list_links = List_with_hornbach) #
    
    # Read Excelfile extracted new products data 
    print('-->>  Read Excelfile extracted new products data [with_Hornbach]')
    df_new_products_with_Hornbach = Tools.read_xlsx_file('\Temp_Output.xlsx')
    print('--- >>>Table of New Products with Hornbach')
    print(tabulate(df_new_products_with_Hornbach, headers='keys', tablefmt='pretty'))
    new_products_list_dicts_with_Hornbach = df_new_products_with_Hornbach.to_dict(orient='records')
    new_products_list_dicts_with_Hornbach
    # store new products links to database 
    print('store new products links to database [with_Hornbach]')
    # LINE 1429
    Database_Mangment.Add_Records_to_Database_New_products_spider(new_products_list_dicts_with_Hornbach)
    
    ###################################################
    ''' [3] --- >>> List_with_Otto '''
    # Delete existing excel files 
    print('-->>  Delete existing excel files ')
    Tools.delete_old_xlsx_files() 
    
    # Run crawler for get all new products details
    print('-->>  Running New ProductsSpider for getting all details about new products [Otto Products]')
    yield runner.crawl(Spiders.ProductsSpider,list_links = List_with_otto) #
    
    # Read Excelfile extracted new products data 
    print('-->>  Read Excelfile extracted new products data [OTTO]')
    df_new_products_with_OTTO = Tools.read_xlsx_file('\Temp_Output.xlsx')
    print('--- >>>Table of New Products with OTTO')
    print(tabulate(df_new_products_with_OTTO, headers='keys', tablefmt='pretty'))
    new_products_list_dicts_with_OTTO = df_new_products_with_OTTO.to_dict(orient='records')
    new_products_list_dicts_with_OTTO
    # store new products links to database 
    print('store new products links to database [OTTO]')
    # LINE 1429
    Database_Mangment.Add_Records_to_Database_New_products_spider(new_products_list_dicts_with_OTTO)
    
    ######################################################

    merged_df_all_new_products = pd.concat([df_new_products_with_krannich, df_new_products_without_krannich,df_new_products_with_Hornbach,df_new_products_with_OTTO], ignore_index=True)
    print('--- >>>Table of New Products')
    print(tabulate(merged_df_all_new_products, headers='keys', tablefmt='pretty'))
    # # store the new records in google sheet - sheet name : Neue Produkte
    print('store the new records in google sheet - sheet name : Neue Produkte')
    Google_sheets.write_NEW_PRODUCTS_to_google_sheets(merged_df_all_new_products)
        
    # sorting new products sheet
    sorting_new_products_sheet().Main_Sorting()
    
    reactor.stop()
    print('\n'*7)
    Tools.sending_email('success')
    print('Ending Crawling Engine ...')
    Tools.draw_final()
    
if __name__ == '__main__':
    print('-->> 2')
    # Run IP rotation in background
    ip_thread = threading.Thread(target=IP_Rotations.rotation_manger_deducted_ip)
    # This ensures that the background thread will automatically stop when the main program exits
    ip_thread.daemon = True
    ip_thread.start()
    
    
    # waiting 3 minutes untill the vpn loading is done and stable
    time.sleep(180)
    
    # Run the data scraping in the main thread
    Main()
    reactor.run()  
     
    

  

# Email addresses : ramezrasmy876@gmail.com
# Upwork Page     : https://www.upwork.com/fl/ramezr
