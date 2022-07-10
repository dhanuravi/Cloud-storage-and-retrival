#################################### DOCUMENTATION BLOCK ################################
'''
Goal    : Python script to store file to local storage
Title   : Python script to store file to local storage
Details : Python script to store file to local storage and to get details about the files
Author  : @Sri Dhanuja
Date	: 01-07-2022
'''

################################# LINK BLOCK #########################################
import os
import gc
import shutil
import uuid
from icecream import ic
from upload_cloud import STORAGE_BUCKET
import traceback

################################ GLOBAL DECLARATION #############################
bucket_adapter = STORAGE_BUCKET()

################################ USER DEFINED CLASS #############################
class UPLOADER:

    def __init__(self) -> None:
        pass

    def UniqueFileID(self):
        return str(uuid.uuid4())

    def file_saver(self,storage,freq):
        folder_path = self.UniqueFileID()
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        os.makedirs(folder_path)
        total_file_size = 0
        total_files = 0
        
        print("UPLOADED FILES : ", end="")
        unwanted_files = []
        wanted_files = []
        for file_ind, (_, files_sent) in enumerate(freq):
                file_name = files_sent.filename
                file_name = file_name.encode('ascii', 'ignore').decode()
                file_name = file_name.replace(" ", "")
                print(file_name, end=", ")
                file_name, extension = os.path.splitext(file_name)
                print(file_name, extension)
                if extension not in ['.pdf', '.PDF', '.img', '.jpg', '.imeg', '.jpeg', '.png', '.tif', '.tiff','.zip']:
                    unwanted_files.append(file_name+extension)
                    continue
                
                file = file_name+extension
                wanted_files.append(file)
                files_sent.save(os.path.join(folder_path, file))
                
                file_stat = os.stat(os.path.join(folder_path, file))
                total_file_size += file_stat.st_size / 1000
                total_files += 1
        status = bucket_adapter.upload(folder_path, storage)
        shutil.rmtree(folder_path)
        if status != -2:
            return total_files, total_file_size, wanted_files, unwanted_files
        else:
            return -2
