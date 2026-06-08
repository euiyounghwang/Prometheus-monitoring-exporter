import concurrent.futures
import time
import multiprocessing
import pandas as pd
import numpy as np
from threading import Thread
import warnings

warnings.filterwarnings("ignore")


def square_number(n):
    ''' 
    array value : 10000000
    array value : 11000000
    array value : 12000000
    array value : 13000000
    '''
    start_time = time.time()
    
    print(f"array value : {n}")

    # time.sleep(1) # 무거운 연산을 시뮬레이션
    # data = sum(i * i for i in range(n))
    data = 0
    for element in n:
        print(f"-- {element} --")
        data += sum(i * i for i in range(element))
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"square_number process - Elapsed Time: {elapsed_time} seconds")

    # return n * n

    # Perform heavy calculations here
    # return sum(i * i for i in range(n))
    return data


# numbers = [10_000_000, 11_000_000, 12_000_000, 13_000_000]
numbers = [[10_000_000, 3], [11_000_000], [12_000_000], [13_000_000]]

def multiple_process():
    ''' 
    Total available logical cores: 12
   
    Single process - Elapsed Time: 3.288329839706421 seconds
    Single process - Elapsed Time: 3.495461940765381 seconds
    Single process - Elapsed Time: 3.860304832458496 seconds
    Single process - Elapsed Time: 4.124040603637695 seconds
    [333333283333335000000, 443666606166668500000, 575999928000002000000, 732333248833335500000]
    Tasks completed

    Array-based : [333333283333335000005, 443666606166668500000, 575999928000002000000, 732333248833335500000]
    '''
    print(f"\n--multiple_process_run - start")
    start_time = time.time()

    # ProcessPoolExecutor를 사용하여 병렬 처리
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        # map 함수는 입력 순서대로 결과를 반환
        results = executor.map(square_number, numbers)
        print(list(results))
        # for result in results:
        #     print(result)

    '''
    processes = []
    # 5개의 프로세스 생성 및 시작
    for i in range(5):
        p = multiprocessing.Process(target=square_number, args=(i,))
        processes.append(p)
        p.start()

    # 모든 프로세스가 끝날 때까지 대기
    for p in processes:
        p.join()
    '''
    print("Tasks completed.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"multiple_process_run - Elapsed Time: {elapsed_time} seconds")


def threads_run():
    
    def work(args):
        for i in [square_number(args)]:
            print(i)

    print(f"\n--threads_run - start")
    start_time = time.time()

    T = []
    th1 = Thread(target=work, args=([10_000_000, 3, 11_000_000, 12_000_000, 13_000_000], ))
    th1.daemon = True
    th1.start()
    T.append(th1)

    for t in T:
        while t.is_alive():
            t.join(0.5)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"threads_run - Elapsed Time: {elapsed_time} seconds")



def split_data_frame():
    '''
    --- DataFrame 1 --- 
        name  age         city
    0  Alice   30     New York
    1    Bob   25  Los Angeles
    to_Json : [{"name":"Alice","age":30,"city":"New York"},{"name":"Bob","age":25,"city":"Los Angeles"}]

    --- DataFrame 2 --- 
        name  age     city
    2  Charlie   35  Chicago
    to_Json : [{"name":"Charlie","age":35,"city":"Chicago"}]

    --- DataFrame 3 --- 
    name  age      city
    3  test   35  Chicago1
    to_Json : [{"name":"test","age":35,"city":"Chicago1"}] 
    '''
    # df = pd.DataFrame({"Item": ["A", "B", "A", "B"], "Value": [1, 2, 3, 4]})
    json_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"},
        {"name": "test", "age": 35, "city": "Chicago1"}
    ]

    df = pd.DataFrame(json_data)

    # 리스트 균등 분할
    n = 3
    chunks = [json_data[i:i + n] for i in range(0, len(json_data), n)]
    # print(f"chunks : {chunks}")

    # 1. np.array_split 활용: N개로 최대한 균등하게 분할
    N = 3
    # N = multiprocessing.cpu_count()
    split_dfs = np.array_split(df, N)

    for i, d in enumerate(split_dfs):
        print(f"--- DataFrame {i+1} --- \n{d}")
        print(f"to_Json : {d.to_json(orient='records')}\n")

    '''
    # Group by the 'Item' column
    grouped = df.groupby("Item")

    # Extract a specific DataFrame group
    df_a = grouped.get_group("A")
    print(df_a)
    print(df_a.to_json())
    '''


if __name__ == '__main__': # Windows 환경에서는 필수
    ''' CPU의 여러 코어를 활용하여 병렬 처리 '''

    ''' os.cpu_count()'''
    print(f"Total available logical cores: {multiprocessing.cpu_count()}")

    ''' Split Data Frame Test'''
    split_data_frame()

    ''' Multiple Prcesss Test'''
    multiple_process()

    ''' Threads'''
    threads_run()
