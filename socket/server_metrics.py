import psutil
import warnings
import logging
import pytz
from flask import Flask, render_template
from datetime import datetime, timedelta
import sys
import time
from threading import Thread
warnings.filterwarnings("ignore")


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("Server_Metrics")

app = Flask(__name__)

tracking_dict = {

}

# PRINTOUT = True
PRINTOUT = False

@app.route('/')
def hello():
    # return render_template('./index.html', host_name=socket.gethostname().split(".")[0], linked_port=port, service_host=env_name)
    return {
        "app" : "server_metrics.py",
        "started_time" : datetime.now(),
        "metrics": [
            {
               "message" : "server_metrics.py",
                "tracking" : tracking_dict
            }
        ]
    }


def get_disk_usage(dir):
    
    # Use '/' for Linux/macOS or 'C:\\' for Windows
    usage = psutil.disk_usage(dir)

    if PRINTOUT:
        print('\n')
        print(f"Total Space: {usage.total / (1024**3):.2f} GB")
        print(f"Used Space:  {usage.used / (1024**3):.2f} GB")
        print(f"Free Space:  {usage.free / (1024**3):.2f} GB")
        print(f"Percentage:  {usage.percent}%")


def get_cpu_memory():
    ''' Get cpu & memory info using psutil library'''
    # Get CPU usage percentage over a 1-second interval
    cpu_pct = psutil.cpu_percent(interval=1)

    # Get overall system memory details
    memory = psutil.virtual_memory()

    if PRINTOUT:
        print("\n")
        print(f"System CPU Usage: {cpu_pct}%")
        print(f"System RAM Usage: {memory.percent}%")
        print(f"Available RAM: {memory.available / (1024**3):.2f} GB")

    # --- CPU Information ---
    ''' To get the total system CPU and memory specifications using the Python psutil library, you can use psutil.cpu_count() to get the number of processor cores and psutil.virtual_memory().total to fetch the total RAM capacity.'''
    # Total logical CPU cores (threads)
    cpu_cores_logical = psutil.cpu_count() 
    # Total physical CPU cores (hardware cores)
    cpu_cores_physical = psutil.cpu_count(logical=False) 
    # Current overall CPU usage percentage (tracked over 1 second)
    cpu_usage_percent = psutil.cpu_percent(interval=1) 

    # --- Memory (RAM) Information ---
    memory_stats = psutil.virtual_memory()
    # Total system memory in bytes
    total_memory_bytes = memory_stats.total 
    # Convert bytes to Gigabytes (GB) for readability
    total_memory_gb = total_memory_bytes / (1024 ** 3) 
    # Current memory utilization percentage
    memory_usage_percent = memory_stats.percent 

    # --- Output Results ---
    if PRINTOUT:
        print('\n')
        print(f"Logical CPU Cores: {cpu_cores_logical}")
        print(f"Physical CPU Cores: {cpu_cores_physical}")
        print(f"Current CPU Usage: {cpu_usage_percent}%\n")

        print(f"Total System Memory: {total_memory_gb:.2f} GB")
        print(f"Current Memory Usage: {memory_usage_percent}%")

    tracking_dict.update({"cpu_cores_logical" : cpu_cores_logical, "cpu_cores_physical" : cpu_cores_physical, "total_memory_gb" : float(str(round(total_memory_gb, 2))), "cpu_usage_percent" : cpu_pct, "ram_usage_percent" : memory.percent})

def work():

    while True:
        
        # logger.info(f"Collecting..")

        ''' Get CPU/Memory'''
        ''' 
        // set
        // lscpu
        // grep -c processor /proc/cpuinfo
        // free -g
        // df -kH /apps
        '''
        get_cpu_memory()

        ''' Get Disk Usage'''
        get_disk_usage("/")

        time.sleep(10)



if __name__ == '__main__':
    """
    Running this service allows us to check the CPU/Memory Info's
    python ./server_metrics.py

    ********* Installation for local env's *******
    sudo su -l <user>
    cd monitoring/metrics_socket
    python -V
    python -m venv .venv
    pip install -r ./dev_requirements_metrics.txt
    ./server_metrics.sh start
    *******************************

    """

    global gloabal_default_timezone

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
        from waitress import serve
        _port = 1111
        serve(app, host="0.0.0.0", port=_port)
        logger.info(f"# Flask App's Port : {_port}")

        for t in T:
            while t.is_alive():
                t.join(0.5)
        # work(target_server)
   
    except Exception as e:
        logger.error(e)