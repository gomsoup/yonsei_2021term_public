from flask import request, current_app
from flask.json import jsonify
from sqlalchemy.sql.functions import session_user
from controller.fcm import sendPackageReceivedMessage, sendArgentMessage
from model.db import PackageInfoWithLog
from flask_restx import Resource
from werkzeug.utils import secure_filename

from model.db import db, PackageInfoWithImage
from model.communicate import *
from resources.ErrorHandler import *

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey


currentStatus = NOTIFY_IDLE

@communicator.route('/',
    doc={
        "description": "Alias for /, this route is being phased out",
        "deprecated": True,
    },)
# 사진 업로드 라우팅. 사진 정보와 디테일을 POST로 전송한다
class Communicator(Resource):
    @communicator.doc()
    @communicator.expect(parser)
    @communicator.response(200, 'Success', upload_res_success_model)
    @communicator.response(400, 'User-Side Failed', upload_res_failed_with_dev_model)
    @communicator.response(500, 'Server-Side Failed', upload_res_server_failed_with_dev_model)
    def post(self):
        if request.mimetype != 'multipart/form-data':
            raise UserInputError("Content-type is not multipart/form-data MIME type!", 'user request header error')

        if 'image' not in request.files:
            raise UserInputError("input is empty", "user did't upload image file")
        
        if request.form.get('message') is None:
            raise UserInputError("message is empty", "user did't post message number")
        
        msg = request.form.get('message')
        file = request.files['image']
        file_ext = file.filename.split('.')[-1]

        print(file_ext)
        if file_ext not in ALLOWED_EXTENSIONS:
            raise UserInputError("not allowed input extention", "user upload forbidden file extention")

        try:
            filename = secure_filename(file.filename)
            file.save(current_app.config['UPLOAD_FOLDER '] + '\\' + filename)
        except:
            raise ServerGeneralError("Internal Server Error", "error occured while saving image file")

        image_db_data = PackageInfoWithImage(image_name = filename, image_msg=msg)

        try:
            db.session.add(image_db_data)
            db.session.commit()
            
        except:
            raise ServerGeneralError("Internal Server General Error", "error while commit image info to databse")
        
        '''
            추후 앱에 notify를 주는 코드 구현 필요
            notify시 foreign key로 notify message와 join 형성
        '''

        return jsonify({'ret' : 'Success'})

@communicator.route('/arduino', methods=['POST', 'GET'])
# 아두이노에서 ARGENT request를 처리하는 라우트. 
# POST로 전송되었을 때는 arduino에서 보내는 msg를 수신.
# GET으로 전송되었을 때는 arduino에서 현재 상태를 확인하는 것으로 현재 상태 반환
class CommunicateArduino(Resource):
    @communicator.doc()
    @communicator.expect(arduino_post_parser)
    @communicator.response(200, 'Success', upload_res_success_model)
    @communicator.response(400, 'User-Side Failed', upload_res_failed_with_dev_model)
    @communicator.response(500, 'Server-Side Failed', upload_res_server_failed_with_dev_model)
    def post(self):
        global currentStatus

        if request.form.get('message') is None:
            raise UserInputError("message is empty", "user did't post message data")
        
        msg = request.form.get('message')

        if(msg == str(DEVICE_ALERT_ARGENT)):
            currentStatus = NOTIFY_ARGENT;
            sendArgentMessage()
            
            log_db_data = PackageInfoWithLog(log_msg="DEVICE_ALERT_ARGENT")
            
            try:
                db.session.add(log_db_data)
                db.session.commit()
            except:
                raise ServerGeneralError("Internal Server General Error", "error while commit log info to databse")
        
        elif(msg == str(DEVICE_PACKAGE_RECEIVED)):
            sendPackageReceivedMessage()

            log_db_data = PackageInfoWithLog(log_msg="DEVICE_PACKAGE_RECIEVED")

            try:
                db.session.add(log_db_data)
                db.session.commit()
            except:
                raise ServerGeneralError("Internal Server General Error", "error while commit log info to databse")
        elif(msg == str(DEVICE_SET_NORMAL)):
            currentStatus = NOTIFY_IDLE;
        elif(msg == str(DEVICE_SET_ARGENT)):
            currentStatus = NOTIFY_ARGENT;


        else:
            raise UserInputError("not allowed msg data", "user sent forbidden numeric")
        
        return jsonify({'ret' : 'Success'})
    
    @communicator.doc()
    @communicator.response(200, 'Success', arduino_get_success_model)
    def get(self):
        description = None
        global currentStatus

        if(currentStatus == APP_SWITCH_ARGENT_MODE):
            description = "APP_SWITCH_ARGENT_MODE"
        elif(currentStatus == APP_SWITCH_NORMAL_MODE):
            description = "APP_SWITCH_NORMAL_MODE"
        elif(currentStatus == NOTIFY_IDLE):
            description = "NOTIFY_IDLE"
        elif(currentStatus == NOTIFY_ARGENT):
            description = "NOTIFY_ARGENT"
        
        ret = jsonify({'currentState' : str(currentStatus), 
                        'Description' : description,
                        'ret' : 'Success'})

        return ret


@communicator.route('/app', methods=['POST', 'GET'])
# 앱에서 status request를 처리하는 route
# POST로 전송되었을 때는 앱에서 status를 업데이트 하는 것
# GET으로 전송되었을 때는 현재까지의 status를 조회하는 것
class CommunicateApp(Resource):
    @communicator.doc()
    @communicator.expect(app_post_parser)
    @communicator.response(200, 'Success', upload_res_success_model)
    @communicator.response(400, 'User-Side Failed', upload_res_failed_with_dev_model)
    @communicator.response(500, 'Server-Side Failed', upload_res_server_failed_with_dev_model)
    def post(self):
        global currentStatus

        if request.form.get('message') is None:
           raise UserInputError("message is empty", "user did't post message data")
        
        msg = request.form.get('message')
        print(msg)
    
        if(msg == str(APP_SWITCH_ARGENT_MODE)):
            currentStatus = APP_SWITCH_ARGENT_MODE;
            
            log_db_data = PackageInfoWithLog(log_msg="APP_SWITCH_ARGENT_MODE")
            try:
                db.session.add(log_db_data)
                db.session.commit()
            except:
                raise ServerGeneralError("Internal Server General Error", "error while commit log info to databse")

        elif(msg == str(APP_SWITCH_NORMAL_MODE)):
            currentStatus = APP_SWITCH_NORMAL_MODE

            log_db_data = PackageInfoWithLog(log_msg="APP_SWITCH_NORMAL_MODE")
            try:
                db.session.add(log_db_data)
                db.session.commit()
            except:
                raise ServerGeneralError("Internal Server General Error", "error while commit log info to databse")

        else:
            raise UserInputError("not allowed msg data", "user sent forbidden numeric")
        
        return jsonify({'ret' : 'Success'})

    def get(self):
        datas = []
        
        try:
            info = PackageInfoWithLog.query.order_by(PackageInfoWithLog.int.desc()).all()
        except:
            raise ServerGeneralError("Internal Server General Error", "error while qeury datas")

        for i in info:
            data = { 'date' : str(i.log_time), 'data' : str(i.log_msg) }
            datas.append(data)

        return jsonify({'ret': 'Success', 'datas' : datas})


