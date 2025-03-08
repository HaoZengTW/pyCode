from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django import template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
import pymysql
import pymysql.cursors
from django.shortcuts import render
from datetime import datetime
import sys
import traceback
import os
from django.conf import settings
from datetime import datetime, timedelta
import json

# cd /Users/dengpeiyu/Desktop/上水汙水處理/rainfall_detect
# python manage.py migrate
# python manage.py runserver
# git init


# 主頁
@csrf_protect
def monitor_table(request):
    result = {'status': 'success', 'msg': '', 'data': []}
    latest_data = None
    try:
        with open("./static/media/link.json", 'r', encoding='UTF-16') as f:
            param = json.load(f)
            connection = pymysql.connect(
                host=param['db']['host'], 
                port=param['db']['port'], 
                user=param['db']['user'], 
                passwd=param['db']['passwd'], 
                db=param['db']['db'], 
                charset='gbk'
            )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # ✅ 修正 SQL，確保 `station_id` 被抓取
        sql = """
        SELECT station_id, station_name, region_name, rainfall_10min, rainfall_1hr, 
               rainfall_3hr, rainfall_6hr, rainfall_12hr, rainfall_24hr, rainfall_2days, 
               data_time, current_time
        FROM `rainfall_web`
        WHERE `data_time` = (SELECT MAX(`data_time`) FROM `rainfall_web`) 
        ORDER BY `rainfall_10min` DESC;
        """
        
        cursor.execute(sql)
        latest_data = cursor.fetchall()  # 獲取該時間點的所有資料

        if latest_data:
            result['data'] = latest_data
            data_time = latest_data[0]['data_time'].strftime('%Y-%m-%d %H:%M:%S')
            result['msg'] = f'成功取得最近 {data_time} 的降雨資料'
            print(result['msg'])
        else:
            result['msg'] = '沒有符合條件的降雨資料'
            print(result['msg'])
            data_time = None

    except Exception as e:
        result['status'] = 'error'
        error_class = e.__class__.__name__
        detail = e.args[0]
        cl, exc, tb = sys.exc_info()
        lastCallStack = traceback.extract_tb(tb)[-1]
        fileName = lastCallStack.filename
        lineNum = lastCallStack.lineno
        funcName = lastCallStack.name
        errMsg = f"File \"{fileName}\", line {lineNum}, in {funcName}: [{error_class}] {detail}"
        result['msg'] = errMsg
        data_time = None


    context = {
        'rainfall_data': result['data'],  # ✅ 確保 `station_id` 會傳遞到前端
        'data_time': data_time
    }

    response = render(request, 'monitor_table.html', context)
    response['Strict-Transport-Security'] = 'max-age=2592000'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    response['Referrer-Policy'] = 'no-referrer'
    response['X-XSS-Protection'] = '1; mode=block'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Strict-Transport-Security'] = 'max-age=16070400; includeSubDomains'
    
    return response

# 選擇觀測測站
@csrf_protect
def select_station(request):
    detect_list = []
    station_list = []

    with open("./static/media/link.json", 'r', encoding='UTF-16') as f:
        param = json.load(f)
        connection = pymysql.connect(
            host=param['db']['host'], 
            port=param['db']['port'], 
            user=param['db']['user'], 
            passwd=param['db']['passwd'], 
            db=param['db']['db'], 
            charset='gbk'
        )
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # SQL 查詢從 detect_condition 表中獲取 station_id
    query = "SELECT station_id, station_name, rainfall_num FROM detect_condition"

    query_station = """
        SELECT * FROM `rainfall_web`
        WHERE `data_time` = (SELECT MAX(`data_time`) FROM `rainfall_web`) 
        ORDER BY `rainfall_10min` DESC;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.execute(query_station)
    station_list = cursor.fetchall()

    # 轉換為字典列表，確保 station_id 不為 None
    detect_list = [
        {
            "station_id": row["station_id"] if row["station_id"] else "UNKNOWN_ID",
            "station_name": row["station_name"], 
            "rainfall_num": row["rainfall_num"] if row["rainfall_num"] else "0"
        }
        for row in rows
    ]

    context = {'detect_list': detect_list, 'station_list': station_list}
    response = render(request, 'select_station.html', context)
    # 設定安全性標頭
    response['Strict-Transport-Security'] = 'max-age=2592000'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    response['Referrer-Policy'] = 'no-referrer'
    response['X-XSS-Protection'] = '1; mode=block'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Strict-Transport-Security'] = 'max-age=16070400; includeSubDomains'
    
    return response

#儲存選擇的測站
@csrf_exempt
def save_selected_stations(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_stations = data.get('selected_stations', [])

            if not selected_stations:
                return JsonResponse({"error": "未收到測站資料"}, status=400)

            with open("./static/media/link.json", 'r', encoding='UTF-16') as f:
                param = json.load(f)

            connection = pymysql.connect(
                host=param['db']['host'],
                port=param['db']['port'],
                user=param['db']['user'],
                passwd=param['db']['passwd'],
                db=param['db']['db'],
                charset='gbk'
            )
            cursor = connection.cursor()

            cursor.execute("DELETE FROM detect_condition")

            for station in selected_stations:
                station_id = station.get("station_id", "UNKNOWN_ID")
                station_name = station.get("station_name", "未知測站")
                rainfall_num = station.get("rainfall_num", "0")

                sql = """
                    INSERT INTO detect_condition (station_id, station_name, rainfall_num) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (station_id, station_name, rainfall_num))

            connection.commit()
            cursor.close()
            connection.close()

            return JsonResponse({"message": "測站已成功儲存至資料庫！"}, status=200)

        except Exception as e:
            print("發生錯誤：", str(e))
            return JsonResponse({"error": str(e)}, status=500)

# 10/23 upgrade    
# 閥門資料表
@csrf_protect
def valve_table(request):
    result = {'status': 'success', 'msg': '', 'data': []}
    latest_data = None
    try:
        # 連接資料庫
        with open("./static/media/link.json", 'r', encoding='UTF-16')as f:
                param = json.load(f)
                connection = pymysql.connect(host=param['db']['host'], port=param['db']['port'], user=param['db']
                                         ['user'], passwd=param['db']['passwd'], db=param['db']['db'], charset='gbk')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 查詢最新的資料
        sql = """SELECT * FROM `valve_table` ORDER BY `valve_close_time` DESC"""
        cursor.execute(sql)
        latest_data = cursor.fetchall()

        # 遍歷查詢結果，處理空值並修改時間格式
        for index, data in enumerate(latest_data):
            # 處理時間欄位的空值
            if latest_data[index]['valve_close_time'] is None:
                latest_data[index]['valve_close_time'] = 'null'
            else:
                # 將字符串轉換為時間格式，並格式化
                if isinstance(latest_data[index]['valve_close_time'], str):
                    latest_data[index]['valve_close_time'] = datetime.strptime(latest_data[index]['valve_close_time'], '%Y-%m-%d %H:%M:%S')
                latest_data[index]['valve_close_time'] = latest_data[index]['valve_close_time'].strftime('%Y-%m-%d %H:%M:%S')

            # 處理 current_time 欄位的空值
            if latest_data[index]['current_time'] is None:
                latest_data[index]['current_time'] = 'null'
            else:
                if isinstance(latest_data[index]['current_time'], str):
                    latest_data[index]['current_time'] = datetime.strptime(latest_data[index]['current_time'], '%Y-%m-%d %H:%M:%S')
                latest_data[index]['current_time'] = latest_data[index]['current_time'].strftime('%Y-%m-%d %H:%M:%S')

            # 檢查其他欄位是否為空，將空值替換為 'null'
            for key in data:
                if latest_data[index][key] is None:
                    latest_data[index][key] = 'null'

        # 檢查是否取得資料
        if latest_data:
            result['data'] = latest_data
            result['msg'] = '成功取得閘門資料'
        else:
            result['msg'] = '無法取得資料'

    except Exception as e:
        result['status'] = 'error'
        error_class = e.__class__.__name__
        detail = e.args[0]
        cl, exc, tb = sys.exc_info()
        lastCallStack = traceback.extract_tb(tb)[-1]
        fileName = lastCallStack.filename
        lineNum = lastCallStack.lineno
        funcName = lastCallStack.name
        errMsg = f"File \"{fileName}\", line {lineNum}, in {funcName}: [{error_class}] {detail}"
        result['msg'] = errMsg

    finally:
        if connection:
            connection.close()

    # 設定 context，並將資料傳遞到前端
    context = {
        'valve_data': result['data']
    }

    # 回傳帶有安全標頭的 response
    response = render(request, 'valve_table.html', context)
    response['Strict-Transport-Security'] = 'max-age=2592000'
    response['X-Frame-Options'] = 'SAMEORIGIN'
    response['Referrer-Policy'] = 'no-referrer'
    response['X-XSS-Protection'] = '1; mode=block'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Strict-Transport-Security'] = 'max-age=16070400; includeSubDomains'
    return response



# 閘門開度表單
@csrf_protect
def monitor_sheet(request):
	response = render(request,'monitor_sheet.html',{})
	response['Strict-Transport-Security'] = 'max-age=2592000'
	response['X-Frame-Options'] = 'SAMEORIGIN'
	response['Referrer-Policy'] = 'no-referrer'
	response['X-XSS-Protection'] = '1; mode=block'
	response['X-Content-Type-Options'] = 'nosniff'
	response['Strict-Transport-Security'] = 'max-age=16070400; includeSubDomains'
	return response


# 10/23 upgrade
# 新增一筆閘門資料
@csrf_exempt
def monitor_sheet_insert(request):
    result = {'status': 'success', 'msg': '', 'data': {}}
    if request.method == 'POST':
        fields = ['valve_close_time', 'before_size', 'before_flow', 'after_size', 'after_flow', 'current_time']
        # 準備資料並確保 POST 中有所有需要的欄位
        sheet_data = request.POST.copy()  # 複製 POST 資料
        sheet_data['current_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 添加 current_time
        try:
            # 建立資料庫連接
            with open("./static/media/link.json", 'r', encoding='UTF-16')as f:
                param = json.load(f)
                connection = pymysql.connect(host=param['db']['host'], port=param['db']['port'], user=param['db']
                                         ['user'], passwd=param['db']['passwd'], db=param['db']['db'], charset='gbk')
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            # 建立 SQL 語句
            sql = f"INSERT INTO `valve_table` ({', '.join([f'`{field}`' for field in fields])}) VALUES ({', '.join(['%s'] * len(fields))});"
            # 從 POST 資料中提取值
            values = [sheet_data.get(field) for field in fields]
            
            # 執行 SQL 語句
            cursor.execute(sql, values)
            connection.commit()  # 提交變更
            result['msg'] = '成功新增一筆資料'

        except Exception as e:
            result['status'] = 'error'
            result['msg'] = str(e)

        finally:
            cursor.close()
            connection.close()

        return JsonResponse(result)
    
    # 如果不是 POST 請求，返回錯誤
    result['status'] = 'error'
    result['msg'] = '請使用 POST 請求'
    return JsonResponse(result)

# 10/23 upgrade
# 刪除閘門紀錄資料
@csrf_exempt
def delete_valve_record(request):
    result = {'status': 'success', 'msg': ''}
    
    if request.method == 'POST':
        try:
            # 從 POST 請求中獲取資料 ID
            record_id = request.POST.get('id')
            # 連接資料庫
            with open("./static/media/link.json", 'r', encoding='UTF-16')as f:
                param = json.load(f)
                connection = pymysql.connect(host=param['db']['host'], port=param['db']['port'], user=param['db']
                                         ['user'], passwd=param['db']['passwd'], db=param['db']['db'], charset='gbk')
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            # 刪除指定的記錄
            sql = "DELETE FROM `valve_table` WHERE `valve_id` = %s"
            cursor.execute(sql, (record_id,))
            connection.commit()

            # 判斷是否成功刪除
            if cursor.rowcount > 0:
                result['msg'] = f'成功刪除此筆資料'
            else:
                result['status'] = 'error'
                result['msg'] = f'找不到此筆資料'

        except Exception as e:
            result['status'] = 'error'
            result['msg'] = str(e)

        finally:
            if connection:
                connection.close()

    else:
        result['status'] = 'error'
        result['msg'] = '僅支持 POST 請求'

    return JsonResponse(result)




