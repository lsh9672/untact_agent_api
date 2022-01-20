import uuid
from datetime import datetime

from flask import request, redirect, Flask, render_template, jsonify, Response, send_file
import requests
from flask_cors import CORS, cross_origin

import binascii

import os
import config as conf
import socket
import ipaddress
from netaddr import IPAddress
import json


app = Flask(__name__)

# CORS처리
CORS(app)

# redirection 링크
# redirect_link = "http://"+conf.ip+":"+conf.jupyter_port+"/lab/tree/"

# 접속유무 확인 - 1이면 사용가능,0이면 사용불가
enable= 1

#리스트 인덱스 0 => fsid, 인덱스 1 => lectureid
sess_dic = {'user1':list(),'user2':list()}
# fsid = None

# 세션 카운트용 2가되면 enable =2
num_of_sess = 0

#확인용 변수
check = 0

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

#장고에 요청해서 디비에 
@app.route('/jupyter-setting', methods = ['POST'])
def set_jupyter():

    global sess_dic         
    global enable
    global num_of_sess

    #장비가 이미 사용중일때 
    if enable == 0:
        return Response(status=400)

    #사용중이지 않을 때 
    elif enable == 1:
        num_of_sess += 1
        if num_of_sess >= 2:
            enable = 0

    #받은 제이슨 데이터
    rev_data = request.json
    
    rev_fsblob = rev_data['fsblob']
    rev_lectureId = rev_data['lectureId']
    rev_userId = rev_data['userId']

    if rev_fsblob is not None:

        workbook_data = rev_fsblob
    else:
        # lectureId의 파일을 열기
        target_workbook = open(conf.lecture_file_path + rev_lectureId + ".ipynb", 'rb')
        workbook_data = target_workbook.read().decode()
        target_workbook.close()

    fsid = uuid.uuid4()

    for i, j in enumerate(list(sess_dic.values())):
        print(len(j))
        if len(j) == 0:
            if i == 0:
                sess_dic['user1'].append(fsid)
                sess_dic['user1'].append(rev_lectureId)
                sess_dic['user1'].append(rev_userId)
            elif i == 1:
                sess_dic['user2'].append(fsid)
                sess_dic['user2'].append(rev_lectureId)
                sess_dic['user2'].append(rev_userId)
            break   
                
    if i == 0:
    # 워크북 파일입력 및 저장
        file = open(conf.ipynb_save_file_path + "user1/workbook.ipynb", 'w')
    elif i == 1:
        file = open(conf.ipynb_save_file_path + "user2/workbook.ipynb", 'w')
    file.write(workbook_data)
    file.close()
    global check
    check = i

    # 교육자료 파일입력 및 저장
    class_data = open(conf.lecture_file_path + rev_lectureId + ".md", 'rb')
    class_book_data = class_data.read().decode()
    class_data.close()
    
    file = open(conf.md_save_file_path, 'w')
    file.write(class_book_data)
    file.close()

    return_result = {'fsid':str(fsid)}

    return json.dumps(return_result) 

@app.route('/jupyter_lab/<userId>/<lectureId>', methods=['GET'])
def get_response(userId, lectureId):
    #try:
    if request.method == 'GET':
        
        # global sess_dic         
        # global enable
        global check

        #장비가 이미 사용중일때 
        # if enable == 0:
        #     return Response(status=400)

        redirect_link = "http://"+conf.device_ip+":"+conf.jupyter_port+"/lab/tree/"
        
        if check == 0:
            temp = redirect_link+"user1/workbook.ipynb"
            return redirect(temp)
        elif check == 1:
            temp = redirect_link+"user2/workbook.ipynb"
            return redirect(temp)
    else:
        return Response(status=404)

    # except Exception as ex:
    #     return Response(status=500)


@app.route('/check_out/<user_name>/', methods=['GET', 'OPTION'])
@cross_origin()
def insert_data(user_name):
    #try:
    # global fsid
    # fsid = sess['fsid']
    global sess_dic
    global enable
    global num_of_sess

    fsid = sess_dic[user_name][0] 
    # save_lectureId = sess['lectureId']
    save_lectureId = sess_dic[user_name][1]

    response_data = ""

    try:
        with open(conf.ipynb_save_file_path + user_name+"/workbook.ipynb", 'rb') as raw_data:
            data = raw_data.read()

            temp_url = "http://"+conf.web_server_ip+":"+conf.web_server_port+"/api/file_data_save"
            
            req_data = {
                'fsid':str(fsid),
                'lectureId':save_lectureId,
                'fsblob':data.decode('utf8')
                }
            
            response_data = requests.post(temp_url,json=req_data)

        # 파일 삭제
        if response_data.status_code == 200:
            if os.path.exists(conf.ipynb_save_file_path + user_name+"/workbook.ipynb"):
                os.remove(conf.ipynb_save_file_path + user_name+"/workbook.ipynb")

            # 접속 가능한 상태로 변경
            if num_of_sess >0:
                num_of_sess -= 1
            if num_of_sess < 2:
                enable = 1
            sess_dic[user_name] = list()
            return str(enable)

        else:
            return Response(status=404)
    except:
        # # 접속 가능한 상태로 변경
        # if num_of_sess >0:
        #     num_of_sess -= 1
        # if num_of_sess < 2:
        #     enable = 1
        # sess_dic[user_name] = list()
        return str(enable)


@app.route('/getMD',methods = ['GET'])
def chap():
    if request.method == 'GET':
        return send_file(conf.md_save_file_path)
    
@app.route('/getCamIp',methods = ['GET'])
def cam():
    if request.method == 'GET':
        return str(conf.camera_ip)

@app.route("/update_time", methods=["GET"])
def update_time():
    global sess_dic

    current_time = datetime.now()

    temp_url = "http://"+conf.web_server_ip+":"+conf.web_server_port+"/api/time_update"
    
    send_list=list()
    for i in sess_dic.values():
        if len(i) != 0:
            req_data = {'fsid':str(i[0])}
            response_data= requests.post(temp_url, json=req_data)

            if response_data.status_code ==200:
                send_list.append(str(i[2]+'/'+str(i[0])+'/'+str(current_time)))


    return jsonify({"data":send_list})

@app.route('/restart',methods=["GET"])
def restart_device():
    global num_of_sess
    global enable
    global sess_dic

    enable = 1
    num_of_sess = 0
    sess_dic['user1'] = list()
    sess_dic['user2'] = list()

    return "restart_success",200

#장비 정보 반환(관리자 페이지)
@app.route('/device_info',methods=["GET"])
def device_info():
    global sess_dic
    
    result_user1 = ""
    result_user2 = ""
    if len(sess_dic['user1']) == 0:
        result_user1 = ""
    else: 
        result_user1 = sess_dic['user1'][2]

    if len(sess_dic['user2']) == 0:
        result_user2 = ""
    else: 
        result_user2 = sess_dic['user2'][2]

    return json.dumps({
        "enable_check":enable,
        "userId1":result_user1,
        "userId2":result_user2,
        "camIp":str(conf.camera_ip)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9672, debug=True)
