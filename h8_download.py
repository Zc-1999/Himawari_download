import os
import re
from datetime import datetime, timedelta
from ftplib import FTP
from tqdm import tqdm
import time

def ftp_operation_wrapper(func):
    def wrapper(self, *args, **kwargs):
        max_retries = 3
        for _ in range(max_retries):
            try:
                return func(self, *args, **kwargs)
            except (EOFError, TimeoutError):
                print("FTP connection lost. Reconnecting...")
                self.reconnect()
        raise ConnectionError(f"Failed to execute FTP operation after {max_retries} attempts.")
    return wrapper

class HimawariDownloader:

    def __init__(self, user, passwd, start_date, end_date, hour_list, output_path):
        self.host = 'ftp.ptree.jaxa.jp'
        self.user = user
        self.passwd = passwd
        self.date_list = self._cal_date_list(start_date, end_date)
        self.hour_list = hour_list
        self.output_path = output_path
        self.connect()

    def _cal_date_list(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        date_list = []
        while start_date <= end_date:
            date_list.append(start_date)
            start_date += timedelta(days=1)
        return date_list

    def connect(self):
        self.ftp = FTP(self.host)
        self.ftp.timeout = 120
        self.ftp.login(self.user, self.passwd)

    def reconnect(self):
        self.disconnect()
        self.connect()

    def disconnect(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp = None

    @ftp_operation_wrapper
    def change_directory(self, path):
        return self.ftp.cwd(path)

    @ftp_operation_wrapper
    def list_files(self):
        return self.ftp.nlst()

    @ftp_operation_wrapper
    def download_file(self, file_name, local_file):
        return self.ftp.retrbinary('RETR ' + file_name, local_file.write)

    def download_from_ftp(self, max_retries=3):
        for date in tqdm(self.date_list, desc='Date_List', position=0):
            for retry in range(max_retries):
                try:
                    parent_path = f'/jma/netcdf/{date.year}{str(date.month).zfill(2)}/{str(date.day).zfill(2)}'
                    self.change_directory(parent_path)
                    files = self.list_files()
                    pattern = re.compile(r'NC_H(08|09)_\d{8}_(\d{2})\d{2}_r14_FLDK\.02701_02601\.nc')
                    matching_files = [file for file in files if pattern.match(file) and pattern.match(file).group(2) in self.hour_list]
                    
                    for file in tqdm(matching_files, desc='Hour_List', position=1):
                        file_path = os.path.join(self.output_path, file)
                        if not os.path.exists(file_path):
                            with open(file_path, 'wb') as local_file:
                                self.download_file(file, local_file)
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"Error: {e}. Retrying ({retry + 1}/{max_retries})...")
                        time.sleep(5)
                    else:
                        print("Reached maximum retries. Giving up.")
                finally:
                    self.change_directory('/')

if __name__ == "__main__":
    config = {
        "user": "",
        "passwd": "",
        "start_date": "2019-01-01",
        "end_date": "2019-01-02",
        "hour_list": ['03', '04', '05'],
        "output_path": "C:/Users/zuochen/Desktop/H8",
    }
    
    downloader = HimawariDownloader(**config)
    downloader.download_from_ftp()
    downloader.disconnect()

