#################################### DOCUMENTATION BLOCK ################################
'''
Goal    : Python class to access Azure,AWS,GCP storage
Title   : Python script to access Azure Storage blobs, AWS s3 bucket, Google cloud buckets
Details : Python script to access Azure Storage blobs, AWS s3 bucket, Google cloud buckets
Author  : @Sri Dhanuja
Date	: 01-07-2022
'''

################################# LINK BLOCK #########################################
import os
import traceback
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient   # to interact with azure storage account, container and blobs
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError     # to handle azure resource related exceptions
import pandas as pd  
from google.cloud import storage
from os import path
import botocore
import logging
import logging.config
import boto3
import pprint

################################# USER DEFINED CLASS #################################

############################# Azure ###############################################

class Azure_Storage:
    ''' Class to wrap Azure APIs '''

    def __init__(self):                                    
        '''  function to initialize azure credentials '''    

        self.connect_str = os.environ['azure_connection_string']
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connect_str)
        self.container_name = os.environ['container_name']
        self.account_url = os.environ['account_url']
        self.credential= os.environ['credential']

    def create_container(self,container_name):      
        ''' function to create conatiner '''        

        try:
            new_container = self.blob_service_client.create_container(container_name)
            print("New Container Created.")

            properties = new_container.get_container_properties()        # Properties of the container
            print(properties)
            return True
        except ResourceExistsError:   
            print("Container already exists.")
            return False

    def delete_container(self,container_name):            
        '''function to delete conatiner '''         

        try:
            self.blob_service_client.delete_container(container_name)
            print("Container Deleted.")
            return True
        except ResourceNotFoundError:  
            print("Container already deleted.")
            return False
    
    
    def list_blobs(self):            
        ''' Function to return names of blobs available in conatiner as a list'''

        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = container_client.list_blobs()
            blobs_list = [blob.name for blob in blob_list]              #getting blob name only in list
            return blobs_list
        except Exception as e:  
            print("Unable to list blobs.")
            return False

    def get_blobs_url(self):      
        ''' Funtion to return blob links of blobs available in conatiner as a list of dict and also to save it to excel '''    

        try:
            print("inside try")
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = container_client.list_blobs()
            blob_url_dict =[]
            for blob in blob_list:
                blob_name = blob.name
                blob_name1 = blob_name.rsplit('/', 1)[-1]                 #getting last value in the blob name
                file_name, extension = os.path.splitext(blob_name1)
                if not extension:                                         #checking if the last value is the virtual folder or file 
                    continue                                              # if not file, go to next blob
                blob = BlobClient(account_url=self.account_url,container_name= self.container_name,blob_name=blob.name,credential=self.credential)  # getting blob url by giving blob name , container , credential
                blob_url_dict.append({"name":blob_name,"file_url":blob.url})

            df = pd.DataFrame(blob_url_dict)

            return blob_url_dict
                
        except Exception as e: 
            print("Unable to list blobs.")
            return e

    def upload(self,local_path,file_name):        
        ''' function to upload blob to the azure'''                                       
        try:                                         
            print("inside try of upload function")                                  
            container = ContainerClient.from_connection_string(self.connect_str, self.container_name)   # Create the BlobServiceClient object which will be used to create a container client
            try:
                container_properties = container.get_container_properties()
            
            except Exception as e:   
                container_client = self.blob_service_client.create_container(self.container_name)
                print(e)
                
            local_path = local_path
            print("local_path",local_path )
            local_file_name = file_name
            print("locak_file_name",local_file_name)
            upload_file_path = os.path.join(local_path,local_file_name)                                                                   
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=local_file_name)  # Create a blob client using the local file name as the name for the blob
            
            print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)
            with open(upload_file_path,"rb") as data:                                        # Upload the created file
                blob_client.upload_blob(data)
                blob_url = blob_client.url
            
            return blob_url
        except Exception as e:
            #print(traceback.print_exc()) 
            return -2
   
    
    def download_using_url(self,dest_path,blob_url):         
        ''' function to download the file using blob url'''
        try:

            blob_url = blob_url
            blob_client = BlobClient.from_blob_url(blob_url=blob_url,credential=self.credential)
            dest_path = dest_path
            blob_name= blob_url.rsplit('/', 2)[-2:]                                             #getting last 2 value as file name (folder and file name)
            print(blob_name)
            blob_name1 = str(str(blob_name[0])+"_"+str(blob_name[1]))
            blob_name1 = str(str(blob_name[1]))
            print(blob_name1)
            DEST_FILE = os.path.join(dest_path,blob_name1)                                      #concatinate dest direct and created file name
            with open(DEST_FILE, "wb") as my_blob:
                download_stream = blob_client.download_blob()                                   # download blob
                my_blob.write(download_stream.readall())
            return 1
        except:
            #logger.error("Error in downloading blob using url",exc_info=True)    
            print(traceback.print_exc())
            return -2




    def delete_single_blob(self,blob_url):     
        ''' function to delete single blob using blob url'''
        try:                                   
            blob_url = blob_url
            blob_client = BlobClient.from_blob_url(blob_url=blob_url,credential=self.credential)
            blob_client.delete_blob()
        except:
            #logger.error("Error in deleting blob",exc_info=True)    
            print(traceback.print_exc())

    def download_using_listofdicturl(self,dest_direct,blob_url_list):  
        ''' funtion to download the blob using the list of dict of blob'''  
        try:

            for each_dict in blob_url_list:
                print(dest_direct)
                print(blob_url_list)
                blob_client = BlobClient.from_blob_url(blob_url=each_dict['file_url'],credential=self.credential)
                DEST_FILE = os.path.join(dest_direct,each_dict['name'])
                with open(DEST_FILE, "wb") as my_blob:
                    download_stream = blob_client.download_blob()
                    my_blob.write(download_stream.readall())
            return "yes"
        except:
            #logger.error("Error in downloading using list of dict url",exc_info=True)    
            print(traceback.print_exc())
    

    def get_folder_name(self,folder_name,dest_direct):     
        
        ''' function to get the folder name as input and return the blob url of the files inside
         the folder as output in list of dict with file name and url '''      
        try:

            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = container_client.list_blobs()
            blob_url_dict =[]
            folder_name = folder_name.strip()  
            folder_name = folder_name +"/" 
            folder_name = folder_name.lower()  
            for blob in blob_list:
                blob_name = blob.name
                if blob_name.lower().find(folder_name)==-1:                                         #checking the folder_name inside the each blob name
                    continue
                blob_name = blob_name.rsplit('/', 1)[-1]
                file_name, extension = os.path.splitext(blob_name)
                if not extension:                                                                   #download the blob which has file in it , ignore virtual blob
                    continue
                blob = BlobClient(account_url=self.account_url,container_name= self.container_name,blob_name=blob.name,credential=self.credential)
                blob_url_dict.append({"name":blob_name,"file_url":blob.url})                        #getting the list of dict of file name and url
            self.download_using_listofdicturl(dest_direct,blob_url_dict)                            #calling download function and saving it in destination folder
            return blob_url_dict
        except:
            #logger.error("Error in getting folder name and downloading based on the folder name",exc_info=True)  
            print(traceback.print_exc())  

    
    def download_blob(self,storage_path,file_name):
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=file_name)

            local_path = storage_path
            download_path = os.path.join(local_path, file_name)

            with open(download_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            print("Blob downloaded.")
            return 1

        except Exception as e:
            print("Unable to download.")
            print(e)
            return -2

       

############################################## CALLING AZURE CLASS ##########################################
#AzureObj = Azure_Storage()
#AzureObj.list_blobs()
# blob_list = AzureObj.get_blobs_url()
#blob_list
#AzureObj.download_using_url(dest_path="./uploads",blob_url="https://exlpoc.blob.core.windows.net/exlpoc/cat.pdf")
#AzureObj.delete_blob("https://exlpoc.blob.core.windows.net/exlpoc/catecate4.jpg")

################################################  GCP #############################################



class Google_storage:

    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket_name = os.environ['bucket_name']
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.bucket.location = os.environ['location'] 
        self.my_bucket = self.storage_client.get_bucket(self.bucket_name)

            
    def download(self,source_blob_name, destination_file_name):
        '''
        Downloads a single file from given s3 path to local path
        
        '''
        try:
            bucket = self.storage_client.get_bucket(self.bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(os.path.join(destination_file_name,blob.name.split('/')[-1]))
        
            print(
                "Blob {} downloaded to {}.".format(
                    source_blob_name, destination_file_name
                )
            )
            return 1
        except:
            ##logger.error("Exception occurred", exc_info=True)
            print(traceback.print_exc())
            return -2

    def download_using_url(self,source_blob_name, destination_file_name):
        '''
        Downloads a single file from given s3 path to local path
        
        '''
        try:
            listblob = source_blob_name.split("/")[-2:]
            bucket = self.storage_client.get_bucket(listblob[0])
            blob = bucket.blob(listblob[1])
            blob.download_to_filename(os.path.join(destination_file_name,blob.name.split('/')[-1]))
        
            print(
                "Blob {} downloaded to {}.".format(
                    listblob[1], destination_file_name
                )
            )
            return 1
        except:
            ##logger.error("Exception occurred", exc_info=True)
            print(traceback.print_exc())
            return -2
#        
    def download_all_files(self,bucket_name,destination_path):
        '''
        Download files from Google bucket to Local
        '''

        try:
            blobs = self.storage_client.list_blobs(self.bucket_name)
            for blob in blobs:
                print(blob.name)
                blob.download_to_filename(os.path.join(destination_path,blob.name.split('/')[-1]))
    
            return {"message": "success", "status": 1}
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
        
    def download_all_folder_files(self,bucket_name,folder_path,local_path):
        '''
        Downloads all files from the specified folder in the given bucket        
        '''        

        bucket = self.storage_client.get_bucket(self.bucket_name)        
        try:
            blobs = bucket.list_blobs(prefix=folder_path)
            for blob in blobs:
                print(blob.name)
                blob.download_to_filename(os.path.join(local_path,blob.name.split('/')[-1]))
    
            return {"message": "success", "status": 1}
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
        
#
    def upload(self,source_file_name, destination_blob_name):
        """Uploads a file to the bucket."""
        try:
            
            bucket = self.storage_client.get_bucket(self.bucket_name)
            dest_blob_name=destination_blob_name
            blob = bucket.blob(dest_blob_name)
    
            blob.upload_from_filename(source_file_name)
            #link = blob.path_helper(self.bucket_name, dest_blob_name)
            gcp_link= "https://storage.cloud.google.com/"+self.bucket_name+"/"+destination_blob_name
            
        
            print(
                "File {} uploaded to {}.".format(
                    source_file_name, destination_blob_name
                )
            )
            return gcp_link
        except:
            #logger.error("Exception occurred", exc_info=True)
            print(traceback.print_exc())
            return -2    

    def delete_folder(self,bucket_name,folder_path):
        '''
        Deletes the given folder and it contents in the bucket        
        '''   
        try:
            bucket = self.storage_client.get_bucket(self.bucket_name)
            blobs = bucket.list_blobs(prefix=folder_path)
            for blob in blobs:
                blob.delete()
            return {"message": "success", "status": 1}
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
        
    def delete(self,bucket_name,blob_path):
        '''
        Deletes a file in the folder of the given bucket        
        '''
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_path)
            blob.delete()
        
            print("Blob {} deleted.".format(blob_path))
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}

################################################### AWS #################################

class AwsS3:
    

    def __init__(self):
        self.bucket_name_aws = os.environ['bucket_name_aws']
        self.client = boto3.client('s3',aws_access_key_id = os.environ['aws_access_key_id'],aws_secret_access_key = os.environ['aws_secret_access_key'])


    def upload(self,local_path,s3_path):
        '''
        In ExtraArgs define your permission and define your bucketname.
        '''
        try:            
            self.local_path = local_path
            self.s3_path = s3_path
            self.bucket_name= self.bucket_name_aws
            location=None
            try:
                location = self.client.get_bucket_location(Bucket=self.bucket_name)['LocationConstraint']
            except:
                self.client.upload_file(local_path, self.bucket_name, s3_path)
                return {"message": "sucess", "status": 1,"url":""}
            self.client.upload_file(self.local_path, self.bucket_name, self.s3_path,ExtraArgs={'ACL': 'public-read'})
            url = "https://s3-%s.amazonaws.com/%s/%s" % (location, self.bucket_name, s3_path)
            #logger.info(url)
            return url
        except:
            #logger.error("Exception occurred", exc_info=True)
            print(traceback.print_exc())
            return "https://s3-us-east-1.amazonaws.com/dhanuaws/%s" % (s3_path)
            

    def delete(self,bucket_name,s3_path):
        '''
        Deletes a file in the folder of the given bucket        
        '''
        try:
            self.bucket_name=bucket_name
            self.s3_path = s3_path
            self.client.delete_object(Bucket=bucket_name, Key=s3_path)
            return {"message": "success", "status": 1}
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
    
    def delete_folder(self,bucket_name,s3_folder_path):
        '''
        Deletes the given folder and it contents in the bucket        
        '''
        try:
            s3 = boto3.resource('s3')
            self.bucket_name=bucket_name
            bucket = s3.Bucket(bucket_name)
            bucket.objects.filter(Prefix=s3_folder_path+"//").delete()
            return {"message": "success", "status": 1}
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
        
    def download(self,s3_path,local_path):
        '''
        Downloads a single file from given s3 path to local path        
        '''
        try:
            self.local_path = local_path+s3_path
            self.s3_path = s3_path
            self.bucket_name=self.bucket_name_aws
            s3 = self.client
               
            s3.download_file(self.bucket_name, self.s3_path, self.local_path)
            
            return 1
        except botocore.exceptions.ClientError as e:
            print(traceback.print_exc())
            if e.response['Error']['Code'] == "404":
                
                print("The object does not exist.")
                return -2
            else:
                return -2

    def download_using_url(self,s3_path_,local_path):
        '''
        Downloads a single file from given s3 path to local path        
        '''
        try:
            s3_path_list = s3_path_.split("/")[-2:]
            s3_path = s3_path_list[1]
            self.local_path = local_path+s3_path
            self.s3_path = s3_path
            self.bucket_name= s3_path_list[0]
            s3 = self.client
               
            s3.download_file(self.bucket_name, self.s3_path, self.local_path)
            
            return 1
        except botocore.exceptions.ClientError as e:
            print(traceback.print_exc())
            if e.response['Error']['Code'] == "404":
                
                print("The object does not exist.")
                return -2
            else:
                return -2
            
    def download_all_files(self,bucket_name,destination_path):
        '''
        download all files from the given bukcet to local path(destination path)        
        '''
        try:
            self.bucket_name=bucket_name
            s3 = boto3.resource('s3')
            # select bucket
            my_bucket = s3.Bucket(bucket_name)
            #download file into current directory
            for s3_object in my_bucket.objects.all():
                filename = s3_object.key                
                my_bucket.download_file(s3_object.key, os.path.join(destination_path,filename)) 
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
        
    def download_all_folder_files(self,bucket_name,folder_path,local_path):
        '''
        Downloads all files from the specified folder in the given bucket        
        '''        
        try:
            s3_resource = boto3.resource('s3')
            my_bucket = s3_resource.Bucket(bucket_name)
            objects = my_bucket.objects.filter(Prefix=folder_path)
            for obj in objects:
                path, filename = os.path.split(obj.key)
                my_bucket.download_file(obj.key,os.path.join(local_path,filename))
            return {"message": "success", "status": 1}
        except:
            #logger.error("Exception occurred", exc_info=True)
            return {"message": "failed", "status": -1}
