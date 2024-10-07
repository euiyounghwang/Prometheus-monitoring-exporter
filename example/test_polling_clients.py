
import datetime
import time
import requests
import json  


def transform_prometheus_txt_to_Json(response):
    ''' transform_prometheus_txt_to_Json '''
    body_list = [body for body in response.text.split("\n") if not "#" in body and len(body)>0]
    
    prometheus_json = {}
    loop = 0
    for x in body_list:
        json_key_pairs = x.split(" ")
        prometheus_json.update({json_key_pairs[0] : json_key_pairs[1]})
            
    print(json.dumps(prometheus_json, indent=2))

    return prometheus_json


def main():
    ''' polling from existing prometheus client'''
    PROMETHEUS = 'http://localhost:9308/'

    end_of_month = datetime.datetime.today().replace(day=1).date()

    last_day = end_of_month - datetime.timedelta(days=1)
    duration = '[' + str(last_day.day) + 'd]'

    response = requests.get(PROMETHEUS + '/metrics',
    #   params={
    #     'query': 'sum by (job)(increase(process_cpu_seconds_total' + duration + '))',
    #     'time': time.mktime(end_of_month.timetuple())}
        )
    
    response = transform_prometheus_txt_to_Json(response)
    print('kafka_brokers - ', response['kafka_brokers'])
   
    # results = response.json()['data']['result']

    # print('{:%B %Y}:'.format(last_day))
    # for result in results:
    #   print(' {metric}: {value[1]}'.format(**result))


if __name__ == "__main__":
    # start_http_server(8003)
    # REGISTRY.register(CustomCollector())
    # while True:
    #     time.sleep(1)
    main()