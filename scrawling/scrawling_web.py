import schedule
import time
import pandas as pd
from datetime import datetime
import pymysql
import requests
import smtplib
from email.mime.text import MIMEText


# =========================
# 文件路徑設置
# =========================
channel_token = "7gY9iU31u3OPNN1UITXYx+zIceIwb2eF+edEb/U0/+vnIgbg7a4xG7g7HAWoNELHeDdlo3pcXWvSKidwT8oDMv+id+p3elkJLUao772waCj6ACQqOXkbrfXt9Gr2o6pgWUUEjAmTBHUvcJ7fzoQuVQdB04t89/1O/w1cDnyilFU="
channel_ID = "C81be0403511b941021a10f89f207a880"
engineer_ID = "Cbe41ce7912b29f6f1648949ac03273a8"
# =========================
# 2. 連接 MySQL 並讀取測站條件
# =========================
def fetch_detect_conditions(connection):
    try:
        with connection.cursor() as cursor:
            query = "SELECT station_id, station_name, rainfall_num FROM detect_condition"
            cursor.execute(query)
            results = cursor.fetchall()
            return {row["station_id"]: {"rainfall_num": row["rainfall_num"], "station_name": row["station_name"]} for row in results}
    except pymysql.MySQLError as e:
        print(f"MySQL 錯誤: {e}")
        return {}

# =========================
# 3. 發送 LINE Notify 訊息
# =========================
def line_message_api(token, to, message):
    """
    使用 LINE Messaging API 發送訊息
    """
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    payload = {
        "to": to,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()


# =========================
# 4. 判斷是否發送 LINE 通知
# =========================
def line_notify_if_needed(stations_to_check, df, connection):
    """
    根據 detect_condition 設定的 station_id 和 rainfall_num 來決定是否發送通知
    """
    # ✅ 初始化記錄
    rainfall_info = []  # 達標測站的通知內容
    log_info = []  # 錯誤或未達標的測站記錄
    notify_log_entries = []  # 存儲通知日誌

    # ✅ 獲取最新 API 回傳的測站 ID 列表
    available_station_ids = df['測站ID'].tolist()

    for station_id, station_data_dict in stations_to_check.items():
        try:
            station_name = station_data_dict["station_name"]
            rainfall_threshold = station_data_dict["rainfall_num"]
            notify_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 若 `station_id` 不在最新抓取的 `df` 內，則不發送通知，但記錄到 log_table
            if station_id not in available_station_ids:
                log_message = f"{station_name} (ID: {station_id}) 測站資料未出現在最新數據中"
                log_info.append(log_message)
                notify_log_entries.append(
                    (station_name, station_id, notify_time, rainfall_threshold, None, 0, log_message)
                )
                continue  # 直接跳過，不發送通知

            # ✅ 提取 `10分鐘` 雨量數據
            station_data = df[df['測站ID'] == station_id]
            rainfall_10min = float(station_data.iloc[0]['10分鐘'])

            # 判斷雨量是否達標
            if rainfall_10min >= rainfall_threshold:
                message = f"{station_name} 測站 ({station_id})雨量達{rainfall_10min} mm"
                rainfall_info.append(message)

        except (ValueError, TypeError) as e:
            error_message = f"{station_name} (ID: {station_id}) 測站數據異常，錯誤訊息: {str(e)}"
            log_info.append(error_message)
            notify_log_entries.append(
                (station_name, station_id, notify_time, rainfall_threshold, None, 0, error_message)
            )

    # ✅ 批量插入日誌
    insert_notify_logs_bulk(connection, notify_log_entries)

    # ✅ 發送通知（只通知超過門檻的測站）
    if rainfall_info:
        send_success_notification(channel_token, rainfall_info)

    # ✅ 不發送工程通知，只記錄 log

# =========================
# 發送mail通知
# =========================
def send_email(content: str, recipients: list, subject: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "no7notification@gmail.com"
    password = "esvs wrdd eamh uuit"

    message = MIMEText(content, "plain", "utf-8")
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()             
        server.starttls()         
        server.login(sender_email, password)

        server.sendmail(sender_email, recipients, message.as_string())
        print("郵件發送成功!")
    except Exception as e:
        print("郵件發送失敗:", e)
    finally:
        server.quit()

# =========================
# 插入通知記錄至 log_table
# =========================
def insert_notify_logs_bulk(connection, notify_log_entries):
    with connection.cursor() as cursor:
        sql_insert_logs = """
        INSERT INTO `log_table` (`station_name`, `station_id`, `notify_time`, `rainfall_condition`, `rainfall_10min`, `status`, `error_msg`)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(sql_insert_logs, notify_log_entries)
    connection.commit()


# =========================
# 發送成功通知
# =========================
def send_success_notification(token, messages):
    """
    發送成功通知到 LINE 群組
    """
    message = "\n".join(messages)
    detailed_message = f"{message}\n--------------------\n請確認閘門開度是否需要調整。\n\
1. 隨時注意進流水量變化及進流抽水站、調整池水位，視雨量大小控制進流閘門適時調整處理水量。\n\
2. 當雨天（梅雨、颱風、豪大雨）進流水量高於 300m³/hr 以上時，將逐步調整閘門開度，以確保設備運轉正常。\n\
3. 必要時，得關閉進流閘門，以保護進流抽水站設備。"
    line_message_api(token, channel_ID, detailed_message)
    send_email(detailed_message,["haozengtw@gmail.com","kenny.chen@ulpu.com.tw","wrcchi.hung@ulpu.com.tw","lt.huang@ulpu.com.tw"],"上水雨量通知")
    print("達標通知已發送")

# =========================
# 6. 發送錯誤通知
# =========================
def send_error_notification(token, errors):
    """
    發送錯誤通知到工程團隊
    """
    message = "工程團隊通知：\n" + "\n".join(errors)
    line_message_api(token, engineer_ID, message)
    print("錯誤通知已發送")



# =========================
# 7. 插入數據到 rainfall_web 表
# =========================
def insert_data_to_db(df, connection):
    with connection.cursor() as cursor:
        sql_insert = """
        INSERT INTO `rainfall_web` 
        (`station_name`, `station_id`, `region_name`, `rainfall_10min`, `rainfall_1hr`, `rainfall_3hr`,
        `rainfall_6hr`, `rainfall_12hr`, `rainfall_24hr`, `rainfall_2days`, `data_time`, `current_time`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data_to_insert = [
            (row['測站名稱'], row['測站ID'], row['行政區'], row['10分鐘'], row['1小時'], row['3小時'], row['6小時'],
             row['12小時'], row['24小時'], row['2天前'], row['資料時間'], row['當前時間'])
            for _, row in df.iterrows()
        ]
        cursor.executemany(sql_insert, data_to_insert)

# =========================
# 8. 主函式：抓取數據、檢查與通知
# =========================
def fetch_and_store_data():
    api_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001?Authorization=rdec-key-123-45678-011121314"

    connection = pymysql.connect(
                host='mysql_service',
                user='num7',
                password='1qaz2wsx',
                database='water_monitor',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
                )
    stations_to_check = fetch_detect_conditions(connection)

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()
        records = data.get('records', {}).get('Station', [])

        extracted_data = [
            {
                '測站名稱': loc.get('StationName', 'N/A'),
                '測站ID': loc.get('StationId', 'N/A'),
                '行政區': loc.get('GeoInfo', {}).get('TownName', 'N/A'),
                '10分鐘': loc.get('RainfallElement', {}).get('Past10Min', {}).get('Precipitation', '0'),
                '1小時': loc.get('RainfallElement', {}).get('Past1hr', {}).get('Precipitation', '0'),
                '3小時': loc.get('RainfallElement', {}).get('Past3hr', {}).get('Precipitation', '0'),
                '6小時': loc.get('RainfallElement', {}).get('Past6hr', {}).get('Precipitation', '0'),
                '12小時': loc.get('RainfallElement', {}).get('Past12hr', {}).get('Precipitation', '0'),
                '24小時': loc.get('RainfallElement', {}).get('Past24hr', {}).get('Precipitation', '0'),
                '2天前': loc.get('RainfallElement', {}).get('Past2days', {}).get('Precipitation', '0'),
                '資料時間': loc.get('ObsTime', {}).get('DateTime', 'N/A'),
                '當前時間': datetime.now().strftime('%Y-%m-%d %H:%M:%S')            }
            for loc in records if loc.get('GeoInfo', {}).get('CountyName', '') == "新竹縣"
        ]

        if extracted_data:
            df = pd.DataFrame(extracted_data).replace('-', None)
            line_notify_if_needed(stations_to_check, df, connection)
            insert_data_to_db(df, connection)
            connection.commit()

    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        connection.close()

# =========================
# 9. 設置定時任務
# =========================
schedule.every(10).minutes.do(fetch_and_store_data)

# =========================
# 10. 持續運行
# =========================
while True:
    schedule.run_pending()
    time.sleep(1)