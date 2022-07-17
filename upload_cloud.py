#################################### DOCUMENTATION BLOCK ################################
'''
Goal    : Python script to call cloud upload function
Title   : Python script to call cloud upload function
Details : Python script to check the cloud storage name and call the respective upload function
Author  : @Sri Dhanuja
Date	: 01-07-2022
'''

################################# LINK BLOCK #########################################
import glob
import os
import traceback
from icecream import ic
from Access_Storage import   Azure_Storage, AwsS3, Google_storage
import zipfile
import uuid

################################ GLOBAL DECLARATION #############################
azure_storage = Azure_Storage()
aws_storage = AwsS3()
gcp_storage = Google_storage()


################################ USER DEFINED CLASS #############################
class STORAGE_BUCKET:
    def __init__(self) -> None:
        self.storage = "azure_storage"
    
    def upload(self, local_folder_path,storage):
        import glob
        files = glob.glob(os.path.join(local_folder_path, '*'))
        for file in files:
            # print(file)
            local_path, file_name = os.path.split(file)
            ic(local_path, file_name)
            if storage == "azure_storage":
                try:
                    status = azure_storage.upload(local_path, file_name)
                    return status
                except:
                    print(traceback.print_exc())
                    #print(e.response)
                    return -2
            if storage == "aws_storage":
                try:
                    status = aws_storage.upload(file, file_name)
                    return status
                except:
                    print(traceback.print_exc())
                    return -2
            if storage == "gcp_storage":
                try:
                    status = gcp_storage.upload(file, file_name)
                    return status
                except:
                    print(traceback.print_exc())
                    return -2

    def upload_using_url(self, local_folder_path,storage):
        import glob
        files = glob.glob(os.path.join(local_folder_path, '*'))
        for file in files:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                new_folder = str(uuid.uuid4())
                if not os.path.isdir(new_folder):
                    os.makedirs(new_folder)
                zip_ref.extractall(new_folder)

        files_new = glob.glob(os.path.join(new_folder, '*'))
        link_list = []
        for file in files_new:
            print(file)
            local_path, file_name = os.path.split(file)
            ic(local_path, file_name)
            
            if storage == "azure_storage":
                try:
                    status = azure_storage.upload(local_path, file_name)
                    link_list.append(status)
                except:
                    print(traceback.print_exc())
                    #print(e.response)
                    return -2
            if storage == "aws_storage":
                try:
                    status = aws_storage.upload(file, file_name)
                    link_list.append(status)
                except:
                    print(traceback.print_exc())
                    return -2
            if storage == "gcp_storage":
                try:
                    status = gcp_storage.upload(file, file_name)
                    link_list.append(status)
                except:
                    print(traceback.print_exc())
                    return -2

        return link_list

            
        
