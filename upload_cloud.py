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
                    if status == -2:
                        return status
                    else:
                        return local_folder_path
                except:
                    print(traceback.print_exc())
                    #print(e.response)
                    return -2
            if storage == "aws_storage":
                try:
                    status = aws_storage.upload(file, file_name)
                    if status == -2:
                        return status
                    else:
                        return local_folder_path
                except:
                    print(traceback.print_exc())
                    return -2
            if storage == "gcp_storage":
                try:
                    status = gcp_storage.upload(file, file_name)
                    if status == -2:
                        return status
                    else:
                        return local_folder_path
                except:
                    print(traceback.print_exc())
                    return -2

            
        
