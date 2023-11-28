import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import paramiko
import os
import threading
import time
from configparser import ConfigParser
import logging

class SFTPTransferApp:
    def __init__(self, root):
        self.root = root
        self.load_config()  # 讀取設定檔

        self.root.title("SFTP文件傳輸")
        self.root.geometry('200x70')
        self.timer_thread = None        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

    
        self.choice_page = ttk.Frame(self.notebook)
        self.notebook.add(self.choice_page, text="選擇動作")
        self.create_choice_page()
        logging.basicConfig(filename='sftp_autofile.log',filemode='w',level=logging.DEBUG,format='%(asctime)s %(levelname)s : %(message)s',encoding='utf-8')


    def load_config(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.host = self.config.get('SFTP', 'host')
        self.username = self.config.get('SFTP', 'username')
        self.userpassword = self.config.get('SFTP', 'userpassword')
        self.local_upload_folder = self.config.get('Folders', 'local_upload_folder')
        self.remote_upload_folder = self.config.get('Folders', 'remote_upload_folder')
        self.local_download_folder = self.config.get('Folders', 'local_download_folder')
        self.local_download_folder2 = self.config.get('Folders', 'local_download_folder2')
        self.local_download_folder3 = self.config.get('Folders', 'local_download_folder3')
        self.remote_download_folder = self.config.get('Folders', 'remote_download_folder')
        self.remote_download_folder2 = self.config.get('Folders','remote_download_folder2')
        self.remote_download_folder3 = self.config.get('Folders','remote_download_folder3')

 
    def save_config(self):
        self.config.set('SFTP', 'host', self.host)
        self.config.set('SFTP', 'username', self.username)
        self.config.set('SFTP', 'userpassword', self.userpassword)
        self.config.set('Folders', 'local_upload_folder', self.local_upload_folder)
        self.config.set('Folders', 'remote_upload_folder', self.remote_upload_folder)
        self.config.set('Folders', 'local_download_folder', self.local_download_folder)
        self.config.set('Folders','local_download_folder2', self.local_download_folder2)
        self.config.set('Folders','local_download_folder3', self.local_download_folder3)
        self.config.set('Folders', 'remote_download_folder', self.remote_download_folder)
        self.config.set('Folders', 'remote_download_folder2', self.remote_download_folder2)
        self.config.set('Folders', 'remote_download_folder3', self.remote_download_folder3)
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def connect_sftp(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, username=self.username, password=self.userpassword, allow_agent=False, look_for_keys=False)
            self.sftp = ssh.open_sftp()
            print("connect success")
            logging.info("connect success")
        except Exception as e:
            print("connect fail")
            logging.error(f"connect fail: {str(e)}")

    def disconnect_sftp(self):
        self.sftp.close()
        print("disconnect")




    def create_choice_page(self):
        self.upload_button = tk.Button(self.choice_page, text="執行上傳", command=self.run_upload)
        self.upload_button.pack(side='left')

        self.download_button = tk.Button(self.choice_page, text="執行下載", command=self.run_download)
        self.download_button.pack(side='left')
        
        self.stop_button = tk.Button(self.choice_page, text="停止自動化", command=self.stop_auto)
        self.stop_button.pack(side='left')

 
    def run_upload(self):
        self.upload_button.config(state='disabled', text='執行中...', background='gray')  # 禁用按鈕，更改文本和背景色
        self.download_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.timer_thread = threading.Thread(target=self.timer_function_upload)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def run_download(self):
        self.upload_button.config(state='disabled')  # 禁用上傳按鈕
        self.download_button.config(state='disabled', text='執行中...', background='gray')  # 禁用按鈕，更改文本和背景色
        self.stop_button.config(state='normal')  # 啟用停止按鈕
        self.timer_thread = threading.Thread(target=self.timer_function_download)
        self.timer_thread.daemon = True
        self.timer_thread.start()



    def upload_folder(self):
        try:
            self.connect_sftp()
            for filename in os.listdir(self.local_upload_folder):
                local_path = os.path.join(self.local_upload_folder, filename)
                remote_path = os.path.join(self.remote_upload_folder, filename)
                self.sftp.put(local_path, remote_path)
            print("All files have been downloaded successfully")
            logging.info("All files have been downloaded successfully")
        except Exception as e:
            print("upload fali")
            logging.error(f"upload fali: {str(e)}")
        finally:
            self.disconnect_sftp()

    def timer_function_upload(self):
        while getattr(self.timer_thread, "do_run", True):
              try:
                 self.upload_folder()
                 self.save_config()
                 time.sleep(30)
              except Exception as e:
                print("upload error")
                logging.error(f"upload error: {str(e)}")

    def timer_function_download(self):
        while getattr(self.timer_thread, "do_run", True):
              try:
                 self.download_folder()
                 self.save_config()
                 time.sleep(30)
              except Exception as e:
                 print(f"download error: {str(e)}")
                 logging.error(f"download error: {str(e)}")

    def stop_auto(self):
        if self.timer_thread and self.timer_thread.is_alive():
           print("stop")
           logging.info("stop....")
           self.timer_thread.do_run = False  # 停止執行
           try:
              self.timer_thread.join()  # 等待執行緒結束
           except KeyboardInterrupt:
              pass  # 處理由於按下停止按鈕而引起的 KeyboardInterrupt
           print("Automation stopped")
           logging.info("Automation stopped")
        else:
            print("Automation not started")
            logging.info("Automation not started")
        self.upload_button.config(state='normal',text='執行上傳',background='SystemButtonFace')  
        self.download_button.config(state='normal', text='執行下載',background='SystemButtonFace')
    def download_folder(self):
        try:
            self.connect_sftp()
            local_download_folders =[self.local_download_folder,self.local_download_folder2,self.local_download_folder3]
            remote_download_folders=[self.remote_download_folder,self.remote_download_folder2,self.remote_download_folder3]
            for i in range(len(local_download_folders)):
                local_folder=local_download_folders[i]
                remote_folder=remote_download_folders[i]
                self.download_files(local_folder,remote_folder)
            print("All folder successfully")
            logging.info("All folder select")
        except Exception as e:
            logging.error(f"select folders fail:{str(e)}")
        finally:
            self.disconnect_sftp()
    def download_files(self, local_folder, remote_folder):
        try:
           self.connect_sftp()
           files_to_download = self.sftp.listdir(remote_folder)
           for file_to_download in files_to_download:
               remote_path = os.path.join(remote_folder, file_to_download)
               local_path = os.path.join(local_folder, os.path.basename(file_to_download))

            # 檢查遠端檔案是否存在
               try:
                self.sftp.stat(remote_path)
               except FileNotFoundError:
                print(f"Remote file not found: {file_to_download}")
                continue  # 跳過不存在的檔案

               print(f"Downloading file: {file_to_download}")
               self.sftp.get(remote_path, local_path)
           print("All files successfully downloaded")
           logging.info("All files successfully downloaded")
           logging.info("Download Success: All files have been downloaded successfully")
        except Exception as e:
            print("Download failed")
            logging.error(f"Download failed: {str(e)}")
        finally:
           self.disconnect_sftp()


if __name__ == "__main__":
    root = tk.Tk()
    sftp_client = SFTPTransferApp(root)
    root.mainloop()
