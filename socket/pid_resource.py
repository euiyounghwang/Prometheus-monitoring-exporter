import psutil
import time
import subprocess

def get_pids_by_name(process_name):
    pids = []
    # 실행 중인 모든 프로세스 순회
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 프로세스 이름이 일치하는 경우 PID 추가
            print(proc.info)
            if proc.info['name'] == process_name:
                pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return pids


''' get ProcessID'''
def get_command_output(cmd):
    ''' Get PID with process name'''
    try:
        call = subprocess.check_output("{}".format(cmd), shell=True)
        response = call.decode("utf-8")
        # print(response)
        return response
    except subprocess.CalledProcessError:
        pass

def get_cpu_usage_by_pid(pid):
    try:
        # 해당 PID로 프로세스 객체 생성
        p = psutil.Process(pid)

        # 첫 번째 호출에서는 이전 상태가 없으므로 0.0을 반환할 수 있습니다.
        # interval=0.1초 동안 프로세스의 CPU 사용률을 측정합니다.
        cpu_percent = p.cpu_percent(interval=0.1)

        return cpu_percent
    except psutil.NoSuchProcess:
        return f"PID {pid}에 해당하는 프로세스가 존재하지 않습니다."
    except psutil.AccessDenied:
        return f"PID {pid}에 접근할 권한이 없습니다."


target_name = "ps ax | grep -i '/streamprocess_omx.jar' | grep -v grep | awk '{print $1}'"
# found_pids = get_pids_by_name(target_name)
found_pids = get_command_output(target_name)

print(f"found_pids : {found_pids}")

'''
found_pids : 2682231

PID 2682231의 CPU 사용률: 0.0%
'''

if found_pids:
    # 측정할 프로세스 ID(PID) 입력
    target_pid = int(found_pids)

    usage = get_cpu_usage_by_pid(target_pid)
    print(f"PID {target_pid}의 CPU 사용률: {usage}%")
