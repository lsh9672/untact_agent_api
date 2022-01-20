from django.shortcuts import render
from django.http import HttpResponse, response, HttpResponseRedirect
from requests.models import Response
from app.models import Equipment
from rest_framework.decorators import api_view
from concurrent.futures import ThreadPoolExecutor

import netaddr,json,requests

# Create your views here.
def restart_get(query_tuple):
    try:
        ip_str = str(netaddr.IPAddress(query_tuple[0]))
        port_str = str(query_tuple[1])
        url = "http://"+ip_str+":"+port_str+"/restart"
        response_data = requests.get(url,timeout=0.5)
    except requests.exceptions.Timeout as ex:
        # return (query_tuple[0],2)
        return 2
    except requests.exceptions.ConnectionError as ex:
        # return (query_tuple[0],2)
        return 2

    # return (query_tuple[0],1)
    return 1

#
def device_info_get(query_tuple):
    try:
        ip_str = str(netaddr.IPAddress(query_tuple[0]))
        port_str = str(query_tuple[1])
        url = "http://"+ip_str+":"+port_str+"/device_info"
        response_data = requests.get(url,timeout=0.5)
    except requests.exceptions.Timeout as ex:
        return {"enable_check":2,"userId":"","camIp":""}
    except requests.exceptions.ConnectionError as ex:
        return {"enable_check":2,"userId":"","camIp":""}

    if response_data.status_code == 200:
        return eval(response_data.text)
    else:
        return {"enable_check":2,"userId":"","camIp":""}

@api_view(['POST'])
def restart_device(request):
    params = request.data

    rev_equipmentId = int(params['equipmentId'])
    rev_deviceId = int(params['deviceId'])

    return_status = 0

    queries = Equipment.objects.filter(equipmentid = rev_equipmentId).values_list("equipmentip","apiport").all()
    temp_queries = list(queries)

    result = {}

    if rev_deviceId == 0:
        with ThreadPoolExecutor(max_workers=20) as pool:
            response_list = list(pool.map(restart_get,temp_queries))
        
        result['result'] = response_list
        if 1 not in response_list:
            return_status = 0
        else:
            return_status=1

    else:
        device_info = temp_queries[rev_deviceId-1]

        ip_str = str(netaddr.IPAddress(device_info[0]))
        port_str = str(device_info[1])
        url = "http://"+ip_str+":"+port_str+"/restart"

        try:
            response_data = requests.get(url,timeout=0.5)
            return_status = 1

        except requests.exceptions.Timeout as ex:
            return_status = 0
    
    return HttpResponse(json.dumps({"result":return_status}))

#특정 장비 주피터 접속
@api_view(['POST'])
def device_jupyter(request):
    params = request.data
    equip_id = params['equipmentId']
    seq = int(params['number'])

    if seq == 0:
        return HttpResponse("value error\nvalue of number in json must be bigger than zero",status=404)

    queries = Equipment.objects.filter(equipmentid = equip_id).values_list("equipmentip","ideport").all()
    temp_queries = list(queries)

    device_info = temp_queries[seq-1]

    ip_str = str(netaddr.IPAddress(device_info[0]))
    port_str = str(device_info[1])

    return_url = "http://"+ip_str+":"+port_str

    return HttpResponse(return_url)

@api_view(['POST'])
def device_info(request):
    params = request.data
    equip_id = params['equipmentId']

    queries = Equipment.objects.filter(equipmentid = equip_id).values_list("equipmentip","apiport").all()
    temp_queries = list(queries)

    result = {}
    result_list = list()
    if queries:
        with ThreadPoolExecutor(max_workers=20) as pool:
            response_list = list(pool.map(device_info_get,temp_queries))

        # for i in sorted(response_list):
        #     result_list.append(i[1])
        
        # result['result'] = result_list
        result['result'] = response_list
    else:
        return response.Http404

    return HttpResponse(json.dumps(result,ensure_ascii=False))