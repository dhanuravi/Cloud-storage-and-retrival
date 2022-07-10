#################################### DOCUMENTATION BLOCK ################################
'''
Goal    : Python script to call the APIs
Title   : Python script to call the APIs
Details : Python script to call the upload and download APIs
Author  : @Sri Dhanuja
Date	: 01-07-2022
'''

################################# LINK BLOCK #########################################
import os
import traceback
import datetime
import uuid
from flask_cors import CORS
from flask import Flask, jsonify, abort, make_response,request
from flask_restful import Api, Resource, reqparse, fields, marshal
from Access_Storage import   Azure_Storage, AwsS3, Google_storage
from upload_local_storage import UPLOADER

################################ GLOBAL DECLARATION #############################
upload_local = UPLOADER()
azure_storage = Azure_Storage()
aws_storage = AwsS3()
gcp_storage = Google_storage()
app = Flask(__name__)
api = Api(app)
CORS(app)


###########################################################################################

app.config.update(

    DROPZONE_MAX_FILE_SIZE=30000,
    DROPZONE_MAX_FILES=3000,
    DROPZONE_IN_FORM=True,
    DROPZONE_UPLOAD_ON_CLICK=True,
    DROPZONE_UPLOAD_ACTION='upload_document',  # URL or endpoint
    DROPZONE_UPLOAD_BTN_ID='submit',
    JSON_SORT_KEYS = False
)

def UniqueFileID(self):
    return str(uuid.uuid4())

@app.route("/", methods=['GET'])
def test_api_working():
    return ("<h1>API running...</h1>")


@app.route("/api/upload", methods=['POST','GET'])
def upload():
    
    
    try:            
        freq = request.files
        freq = list(freq._iter_hashitems())
        storage= request.form.get('storage_cloud_name')
        print(storage)
        if storage == None:
            storage = "gcp_storage"
        try:
            num_records, total_files_size, files, unwanted_files = upload_local.file_saver(storage,freq)
        
            return make_response(jsonify({
                'message':"uploaded Successfully!!!",
                'accepted_files':files,
                'denied_files': unwanted_files
                }), 200)
        except:
            print(traceback.print_exc())
            return make_response(jsonify({
            'message':"Not able to upload"
            }), 400)
    
    except Exception as e:
        print(traceback.print_exc())
        return make_response(jsonify({
            'message':"Not able to upload"
            }), 400)

@app.route("/api/download_blob_using_name", methods=['POST','GET'])
def download():
    try:
        storage_path = request.form.get('storage_path')
        file_name = request.form.get('blob_name')
        storage_cloud_name = request.form.get('storage_cloud_name')
        if storage_cloud_name == "azure_storage":
            val = azure_storage.download_blob(storage_path,file_name)
            if val == 1:
                return make_response(jsonify({'message':"Successfuly downloaded"}), 200)
            if val == -2:
                return make_response(jsonify({'message':"Not able to download"}), 400)

        if storage_cloud_name == "aws_storage":
            val = aws_storage.download(file_name,storage_path)
            if val == 1:
                return make_response(jsonify({'message':"Successfuly downloaded"}), 200)
            if val == -2:
                return make_response(jsonify({'message':"Not able to download"}), 400)

        if storage_cloud_name == "gcp_storage":
            val = gcp_storage.download(file_name,storage_path)
            if val == 1:
                return make_response(jsonify({'message':"Successfuly downloaded"}), 200)
            if val == -2:
                return make_response(jsonify({'message':"Not able to download"}), 400)
    except:
        print(traceback.print_exc())
        return make_response(jsonify({
            'message':"Not able to download",
            }), 400)


if __name__ == '__main__':
    app.debug = False
    app.run(port=5000, threaded=True)