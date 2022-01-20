from django.shortcuts import render
from django.http import HttpResponse, response, HttpResponseRedirect
from requests.api import request
from requests.models import Response
from app.models import Connectionlog, Equipment,Filedata, Typeofequipment
from rest_framework.decorators import api_view
from concurrent.futures import ThreadPoolExecutor

import netaddr,os,json,requests
from datetime import datetime
import uuid
import binascii


def url_get(query_tuple):

    try:
        ip_str = str(netaddr.IPAddress(query_tuple[0]))
        port_str = str(query_tuple[1])
        url = "http://"+ip_str+":"+port_str+"/enable_check"
        response_data = requests.get(url,timeout=0.5)
        dict_dat = json.loads(response_data.text)
        data = int(dict_dat['enable'])

    except requests.exceptions.Timeout as ex:
        return (query_tuple[0],2)

    return (query_tuple[0],data)

def restart_get(query_tuple):
    try:
        ip_str = str(netaddr.IPAddress(query_tuple[0]))
        port_str = str(query_tuple[1])
        url = "http://"+ip_str+":"+port_str+"/restart"
        response_data = requests.get(url,timeout=0.5)
    except requests.exceptions.Timeout as ex:
        return (query_tuple[0],2)
    except requests.exceptions.ConnectionError as ex:
        return (query_tuple[0],2)

    return (query_tuple[0],1)


# Create your views here.
@api_view(['POST'])
def enable_check(request):
    # try:
    params = request.data
    rev_equipmentId = int(params['equipmentId'])

    # queries = Iptable.objects.filter(equipmentid = rev_equipmentId).values_list("outipaddress","apioutport").all()
    queries = Equipment.objects.filter(equipmentid = rev_equipmentId).values_list("equipmentip","apiport").all()

    enable_list = list()
    # for  query in queries:
    #     ip_str = str(netaddr.IPAddress(query[0]))
    #     port_str = str(query[1])
    #     request_str = "http://"+ip_str+":"+port_str+"/enable_check"
    #     try:
    #         #timeout 단위는 sec
    #         response_data = requests.get(request_str,timeout=0.5)
    #         dict_dat = json.loads(response_data.text)
    #         data = dict_dat['enable']
    #         enable_list.append(int(data))
    #     except requests.exceptions.Timeout as ex:
    #         #장비가 꺼져있어서 timeout이 될경우
    #         enable_list.append(2)
    #     except requests.exceptions.ConnectionError as ex:
    #         enable_list.append(2)

    with ThreadPoolExecutor(max_workers=20) as pool:
        response_list = list(pool.map(url_get,list(queries)))

    # response_list = sorted(response_list)
    # enable_dict = {"enable" : enable_list}
    for i in sorted(response_list):
        enable_list.append(i[1])
        
    enable_dict = {"enable" : enable_list}
    # except Exception as ex:
    #     return response.HttpResponseBadRequest

    return HttpResponse(json.dumps(enable_dict,ensure_ascii=False))

@api_view(['POST'])
def go_to_jupyter(request):
    # try:
    params = request.data
    rev_equipmentId = int(params['equipmentId'])
    rev_userId = params['userId']
    rev_lectureId = params['lectureId']
    rev_number = int(params['number'])

    # queries = Iptable.objects.filter(equipmentid = rev_equipmentId).values_list("outipaddress","apioutport").all()
    queries = Equipment.objects.filter(equipmentid = rev_equipmentId).values_list("equipmentip","apiport").all()

    target_query = queries[rev_number-1]
    temp_ip =netaddr.IPAddress(target_query[0])
    ip_str = str(temp_ip)
    port_str = str(target_query[1])
    request_str = "http://"+ip_str+":"+port_str+"/jupyter_lab/"+rev_userId+"/"+rev_lectureId

    
    #접속하려고 하는 해당 장비번호와 유저아이디로 ConnectionLog 테이블을 조회해서 가장 최근값을 가져옴
    connection_log_query = Connectionlog.objects.filter(
        userid = rev_userId,lectureid=rev_lectureId,equipmentid=rev_equipmentId
        ).values_list("finishtime","fsid").order_by("-finishtime").first()
    
    set_url = "http://"+ip_str+":"+port_str+"/jupyter-setting"

    post_data = dict()
    response_data=""
    post_data['userId'] = rev_userId
    
    #최근값이 있다면 최근에 작업한 파일(FlieData 테이블의 FSBLOB)를 반환함
    if connection_log_query is not None:
        
        target_uuid = connection_log_query[1]
        #최근에 작업한 파일 가져오기(FSBLOB)
        file_data_query = Filedata.objects.filter(fsid = target_uuid).values_list("fsblob").first()

        #있으면 필요한 데이터 담아서 주피터 셋팅 엔드포인트로 post
        if file_data_query is not None:
            if file_data_query[0] is not None:
                temp_fsblob = binascii.unhexlify(file_data_query[0][2:])
                post_data['fsblob'] = temp_fsblob.decode('utf8')
                post_data['lectureId'] = rev_lectureId
                response_data = requests.post(set_url, json=post_data)
            else:
                post_data['fsblob'] = None
                post_data['lectureId'] = rev_lectureId
                response_data = requests.post(set_url, json=post_data)
        #없으면 fsblob에  none
        else:
            post_data['fsblob'] = None
            post_data['lectureId'] = rev_lectureId
            response_data = requests.post(set_url, json=post_data)

    #없다면 fsblob에 none
    else:
        post_data['fsblob'] = None
        post_data['lectureId'] = rev_lectureId
        response_data = requests.post(set_url, json=post_data)

    
    if response_data.status_code != 200:
        return response.Http404

    current_time = datetime.now()
    #파일셋팅이 끝나면 커넥션 로그 저장을 위한 fsid와 생성시 시간을 받ㅇ
    rev_json = response_data.json()
    temp_fsid = uuid.UUID(rev_json['fsid'])

    #db에 저장
    insert_file_data = Filedata(fsid = temp_fsid ,filename=None,fsblob=None)
    insert_file_data.save()

    temp_equ_id=Typeofequipment.objects.get(equipmentid = rev_equipmentId)
    temp_equ_ip = Equipment.objects.get(equipmentip = temp_ip)
    temp_file_fsid = Filedata.objects.get(fsid = temp_fsid)

    #커넥션 로그 생성 및 저장
    new_connection = Connectionlog(userid=rev_userId,equipmentid=temp_equ_id,equipmentip=temp_equ_ip,finishtime=None,lectureid=rev_lectureId,fsid=temp_file_fsid,entertime=current_time)
    new_connection.save()
    # payload = dict()
    # payload["request_str"] = request_str
    # except Exception as ex:
    #     return response.HttpResponseBadRequest

    # return HttpResponse(json.dumps(payload,ensure_ascii=False))

    return HttpResponseRedirect(request_str)

@api_view(['POST'])
def restart_device(request):
    params = request.data

    rev_equipmentId = int(params['equipmentId'])
    rev_deviceId = int(params['deviceId'])

    queries = Equipment.objects.filter(equipmentid = rev_equipmentId).values_list("equipmentip","apiport").all()
    temp_queries = list(queries)

    result = {}

    if rev_deviceId == 0:
        with ThreadPoolExecutor(max_workers=20) as pool:
            response_list = list(pool.map(restart_get,temp_queries))
        
        result['result'] = response_list

    else:
        device_info = temp_queries[rev_deviceId-1]

        ip_str = str(netaddr.IPAddress(device_info[0]))
        port_str = str(device_info[1])
        url = "http://"+ip_str+":"+port_str+"/restart"

        try:
            response_data = requests.get(url,timeout=0.5)

        except requests.exceptions.Timeout as ex:
            return response.Http404

    return HttpResponse("restart_success")


#check_out시 데이터를 저장하는 엔드포인트
@api_view(['POST'])
def file_data_save(request):

    rev_data = request.data
    temp_fsid = uuid.UUID(rev_data['fsid'])
    temp_lectureId = rev_data['lectureId']

    #타입변환 필요 - VARBINARY로
    fsblob = '0x'.encode('ascii')+binascii.hexlify(rev_data['fsblob'].encode('utf8'))

    try:
        #데이터 업데이트 - Filedata
        Filedata.objects.filter(fsid = temp_fsid).update(filename = str(temp_lectureId),fsblob = fsblob)

        #데이터 업데이트 - ConnectionLog
        Connectionlog.objects.filter(fsid = temp_fsid).update(finishtime = datetime.now())

    except:
        return response.Http404

    return HttpResponse("file save successful")


#시간 업데이트 하는 엔드 포인트
@api_view(['POST'])
def time_update(request):

    rev_data = request.data
    temp_fsid = uuid.UUID(rev_data['fsid'])

    try:
        Connectionlog.objects.filter(fsid = temp_fsid).update(finishtime = datetime.now())
    except:
        return response.Http404

    return HttpResponse("update success")








