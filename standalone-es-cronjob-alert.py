import time
import datetime
import threading
import pytz
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, render_template
import argparse
import logging
import os
import sys
import warnings

warnings.filterwarnings("ignore")

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("Tools-Alert-Script")

''' Tracking thread_alert_message '''
tracking_dict = {
    
}


class Util:

    def __init__(self):
        pass
                
    @staticmethod
    def get_json_load(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    
    @staticmethod
    def get_datetime():
        return datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    

def get_week_of_month(target_date):
    # 해당 월의 1일
    first_day = target_date.replace(day=1)
    # 1일의 요일 (월요일: 0 ~ 일요일: 6)
    first_day_weekday = first_day.weekday()
    
    # (현재 일 + 1일의 요일 인덱스) / 7 올림
    import math
    return math.ceil((target_date.day + first_day_weekday) / 7)



app = Flask(__name__)

@app.route('/')
def hello():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "standalone-es-curator.py",
        "started_time" : datetime.datetime.now(),
        "tools": [
            {
               "message" : "standalone-es-cronjob.py",
                "tracking" : tracking_dict
            }
        ]
    }


# 매일 특정 시간에 실행 (예: 10:30)
# schedule.every().day.at("14:46").do(job)

# 스케줄링 작업을 수행하는 별도 스레드 실행
# def start_schedule():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
        

def work():
  ''' Main'''

  while True:
    try:
      print("\n")
      logger.info("** work func ** ")

      _api_host = os.environ.get('API_HOST', 'localhost2')
      logger.info(f"{_api_host}")
      # 오늘 날짜를 YYYY-MM-DD 형식으로 가져오기
      # today = datetime.datetime.today().strftime("%Y-%m-%d")
      # print(today)

      # 오늘 날짜와 시간 가져오기
      now = datetime.datetime.today()

      # 예시: 2026년 8월 28일
      # d = datetime.date(2026, 8, 3)
      d = datetime.date(now.year, now.month, now.day)
      logger.info(f"{d.month}월 {get_week_of_month(d)}주차입니다. {now.weekday()}, {now.strftime('%A')}")

      print("\n")

    # except (KeyboardInterrupt, SystemExit) as e:           
    except Exception as e:
      # logger.error(f"work func : {e}")
      pass
    
    time.sleep(60)
       


if __name__ == "__main__":
    ''' This script will run and sending the alert value via CRONJOB'''
    # schedule_thread = threading.Thread(target = job)
    # schedule_thread.start()

    parser = argparse.ArgumentParser(description="Running this service allows us to check and run the cronjob for the alert using this script")
    parser.add_argument('-port', '--port', dest='port', default=9991, help='port')
    args = parser.parse_args()

    global gloabal_default_timezone

    if args.port:
      _port = args.port
    
    gloabal_default_timezone = pytz.timezone('US/Eastern')
    
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
            
      T = []
      th1 = Thread(target=work, args=())
      th1.daemon = True
      th1.start()
      T.append(th1)

      ''' Expose this app to acesss'''
      ''' Flask at first run: Do not use the development server in a production environment '''
      ''' For deploying an application to production, one option is to use Waitress, a production WSGI server. '''
      # app.run(host="0.0.0.0", port=int(port)-4000)
      from waitress import serve
      serve(app, host="0.0.0.0", port=_port)
      logger.info(f"# Flask App's Port : {_port}")
      
      for t in T:
        while t.is_alive():
            t.join(0.5)

    except Exception as e:
      logger.error(e)