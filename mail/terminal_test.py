import logging
import subprocess
import os
import json
from collections import defaultdict

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def isProcessRunning(self, name):
    ''' Get PID with process name'''
    try:
        call = subprocess.check_output("pgrep -f '{}'".format(name), shell=True)
        logging.info("Process IDs - {}".format(call.decode("utf-8")))
        
        return True
    except subprocess.CalledProcessError:
        return False


def get_run_cmd_Running(cmd):
    ''' Get PID with process name'''
    try:
        logging.info("get_run_cmd_Running - {}".format(cmd))
        call = subprocess.check_output("{}".format(cmd), shell=True)
        output = call.decode("utf-8")
        logging.info("CMD - {}".format(output))
        # logging.info(output.split("\n"))
        
        output = [element for element in output.split("\n") if len(element) > 0]

        return output
    except subprocess.CalledProcessError as e:
        logging.error(e)
        return None     



if __name__ == '__main__':
    ''' import os.environ'''
    ZOOKEEPER_URLS = os.environ["ZOOKEEPER_URLS"]
    BROKER_LIST = os.environ["BROKER_LIST"]

    # kafka_topic_isr = '/home/biadmin/monitoring/custom_export/kafka_2.11-0.11.0.0/bin/kafka-topics.sh --describe --zookeeper  {} --topic ELASTIC_PIPELINE_QUEUE'.format(ZOOKEEPER_URLS)
    GET_KAFKA_ISR_LIST = os.environ["GET_KAFKA_ISR_LIST"]
    response = get_run_cmd_Running(GET_KAFKA_ISR_LIST)

    # logging.info(f"Kafka ISR : {response}")
    ''' ['Topic:ELASTIC_PIPELINE_QUEUE\tPartitionCount:16\tReplicationFactor:3\tConfigs:', '\ '''

    if response:
        kafk_offsets_dict = defaultdict()
        for idx in range(1, len(response)):
            each_isr = [element for element in response[idx].split("\t") if len(element) > 0]
            logging.info(each_isr)
            kafk_offsets_dict.update({"{}_{}".format(each_isr[0],str(idx-1)) : each_isr})
        
        """
        {
            "Topic: ELASTIC_PIPELINE_QUEUE_0": [
                "Topic: ELASTIC_PIPELINE_QUEUE",
                "Partition: 0",
                "Leader: 1",
                "Replicas: 3,1,2",
                "Isr: 1,2"
            ],
            "Topic: ELASTIC_PIPELINE_QUEUE_1": [
                "Topic: ELASTIC_PIPELINE_QUEUE",
                "Partition: 1",
                "Leader: 1",
                "Replicas: 1,2,3",
                "Isr: 1,2"
            ],
            ...
        }
        """
        print(f"kafk_offsets_dict - ", kafk_offsets_dict)
        if isinstance(kafk_offsets_dict, (dict, list)):
            logging.info(f"ISR : {json.dumps(kafk_offsets_dict, indent=2)}")
    else:
        logging.info(f"ISR : {response}")


    logging.info('\n')

    ''' Extract get kafka offsets information'''
    kafka_offset = '/home/biadmin/monitoring/custom_export/kafka_2.11-0.11.0.0/bin/kafka-run-class.sh kafka.tools.GetOffsetShell --topic ELASTIC_PIPELINE_QUEUE --broker-list {}'.format(BROKER_LIST)
    
    response = get_run_cmd_Running(kafka_offset)

    if response:
        kafk_offsets_dict = defaultdict()
        for element in response:
            each_offset = element.split(":")
            # logging.info(f"lenght of each offset : {len(each_offset)}")
            if len(each_offset) > 2:
                kafk_offsets_dict.update({each_offset[1] : each_offset[2]})
            else:
                kafk_offsets_dict.update({each_offset[0] : each_offset[1]})
        
        """
        KAFKA_OFFSET_ISR_INFO : {
            "8": "128985086",
            "11": "126352461",
            "2": "124464369",
            "5": "124956818",
            "14": "122069257",
            "13": "124863594",
            "4": "132063084",
            "7": "124396250",
            "10": "130013071",
            "1": "124465052",
            "9": "127150290",
            "12": "124311886",
            "3": "132353638",
            "15": "126593574",
            "6": "128556033",
            "0": "121912423"
        }
        """
        if isinstance(kafk_offsets_dict, (dict, list)):
            logging.info(f"KAFKA_OFFSET_ISR_INFO : {json.dumps(kafk_offsets_dict, indent=2)}")
    else:
        logging.info(f"KAFKA_OFFSET_ISR_INFO : {response}")
    