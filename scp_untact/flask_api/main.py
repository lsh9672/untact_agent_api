import uuid
from datetime import datetime

from flask import request, redirect, Flask, render_template, jsonify, Response, send_file
from flask_cors import CORS, cross_origin

import binascii
import requests

import os
import config as conf
import ipaddress
from netaddr import IPAddress
import json


app = Flask(__name__)

# CORS처리
CORS(app)

# check_out 엔드포인트 호출시, 파일의 lectureId를 저장하기 위한 변수
save_lectureId = ""

# redirection 링크
# redirect_link = "http://"+conf.ip+":"+conf.jupyter_port+"/lab/tree/workbook.ipynb"

# 접속유무 확인 - 1이면 사용가능,0이면 사용불가
enable = 1

fsid = None

userID=None

@app.route('/enable_check', methods=['GET'])
def show_main():
    try:
        if request.method == 'GET':
            global enable
            return_data = {"enable": enable}
            return jsonify(return_data)
        else:
            return Response(ststus=404)
    except Exception as ex:
        print('error : ', ex)
        return Response(status=500)


@app.route('/jupyter-setting', methods = ['POST'])
def set_jupyter():
    global enable
    #장비가 이미 사용중일떄
    if enable == 0:
        return Response(status=400)

    #사용중이지 않을때
    elif enable == 1:

        enable = 0

        rev_data = request.json

        rev_fsblob = rev_data['fsblob']
        rev_lectureId = rev_data['lectureId']

        # 최근에 작업한 파일이 있다면
        if rev_fsblob is not None:

            workbook_data = rev_fsblob

        else:
            # lectureId의 파일을 열기
            target_workbook = open(conf.lecture_file_path + rev_lectureId + ".ipynb", 'rb')
            workbook_data = target_workbook.read().decode()
            target_workbook.close()

        # 워크북 파일입력 및 저장
        file = open(conf.ipynb_save_file_path, 'w')
        file.write(workbook_data)
        file.close()

        # 교육자료 파일입력 및 저장
        class_data = open(conf.lecture_file_path + rev_lectureId + ".md", 'rb')
        class_book_data = class_data.read().decode()
        class_data.close()

        file = open(conf.md_save_file_path, 'w')
        file.write(class_book_data)
        file.close()

        # 신규 Connection Log 추가를 위한 fsid리턴
        global fsid
        fsid = uuid.uuid4()

        return_result = {'fsid':str(fsid)}

        return json.dumps(return_result)


@app.route('/jupyter_lab/<userId>/<lectureId>', methods=['GET'])
def get_response(userId, lectureId):
    #try:
    if request.method == 'GET':
        # global enable

        # if enable == 0:
        #     return Response(status=400)

        global userID
        userID = userId

        global save_lectureId
        # 파라미터 받기
        save_lectureId = lectureId

        #주소에 들어가는 ip와 port번호는 config파일에서 가져오는 것으로 수정
        redirect_link = "http://"+conf.device_ip+":"+conf.jupyter_port+"/lab/tree/workbook.ipynb"
        return redirect(redirect_link)
    else:
        return Response(status=404)

    # except Exception as ex:
    #     return Response(status=500)


@app.route('/check_out', methods=['GET'])
def insert_data():

    global fsid
    global save_lectureId
    global enable


    response_data=""
    try:
        with open(conf.ipynb_save_file_path, 'rb') as raw_data:
            data = raw_data.read()

            temp_url = "http://"+conf.web_server_ip+":"+conf.web_server_port+"/api/file_data_save"

            req_data = {
                'fsid':str(fsid),
                'lectureId':save_lectureId,
                'fsblob':data.decode('utf8')
                }
            #request모듈을 이용해서 fsid를 보냄
            response_data= requests.post(temp_url, json=req_data)


        if response_data.status_code == 200:

            # 파일 삭제
            if os.path.exists(conf.ipynb_save_file_path):
                os.remove(conf.ipynb_save_file_path)

            # 접속 가능한 상태로 변경
            enable = 1
            return str(enable)
        else:
            return Response(status=404)
    except:
        enable = 1
        return str(enable)

@app.route('/getMD',methods = ['GET'])
def chap():
    if request.method == 'GET':
        return send_file(conf.md_save_file_path)

@app.route('/getCamIp',methods = ['GET'])
def cam():
    return str(conf.camera_ip)
    

@app.route('/update_time', methods=["GET"])
def update_time():
    global userID
    global fsid

    current_time = datetime.now()


    temp_url = "http://"+conf.web_server_ip+":"+conf.web_server_port+"/api/time_update"
    req_date = {'fsid':str(fsid)}
    response_data= requests.post(temp_url, json=req_date)
    
    if response_data.status_code == 200:

        return "success"

    else:
        return Response(status=404)

@app.route('/restart',methods=["GET"])
def restart_device():
    global enable
    global save_lectureId
    global fsid
    global userID
    
    save_lectureId = ""
    enable =1
    fsid = None
    userID=None

    return "restart_success",200

#장비 정보 반환(관리자 페이지)
@app.route('/device_info',methods=["GET"])
def device_info():

    result_userId=""
    if userID == None:
        result_userId = ""
    else:
        result_userId = userID

    return json.dumps({
        "enable_check":enable,
        "userId":result_userId,
        "camIp":conf.camera_ip
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9672, debug=True)
