from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import json
import os
import jaydebeapi, jpype
import sys
from datetime import datetime
from airflow.models import Variable
import logging
from db import oracle_database

logger = logging.getLogger("airflow.task")


current_path = os.path.dirname(os.path.abspath(__file__))

    

''' Add dag in Apache airflow'''
# DAG Definition
dag = DAG(
    dag_id='prometheus_log_dag',
    description='Clear old logs in h2 database',
    # schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 9, 1),
    schedule_interval="00 18 * * *",  # 6:00 PM every day
    catchup=False,
    tags=["Prometheus"]
)


def work(sql, _type):
    """
    query = "SELECT * FROM MONITORING"
    connection  = jaydebeapi.connect(
        "org.h2.Driver",
        "jdbc:h2:tcp://localhost/monitoring/h2/data/monitoring",
        ["test", "test"],
        "../h2-1.4.200.jar")
    cursor = connection.cursor()
    cursor.execute(query)
    if returnResult:
        returnResult = _convert_to_schema(cursor)
    cursor.close()
    connection.close()
    """
    try:
        """ add variables on Airflow admin menu"""
        LOG_DB_USER = Variable.get("LOG_DB_USER")
        LOG_DB_URL = Variable.get("LOG_DB_URL")
        
        logger.info(f"LOG_DB_URL : {LOG_DB_URL}, LOG_DB_USER : {LOG_DB_USER}, LOG_SQL : {sql}")

        db_obj = oracle_database(LOG_DB_USER, LOG_DB_URL)
        db_obj.set_db_connection()
        if _type == "SELECT":
            result_dict = db_obj.select_oracle_query(sql)
        else:
            result_dict = db_obj.excute_oracle_query(sql)
        '''  <class 'list'> <- result_dict '''
        logger.info(json.dumps(result_dict, indent=2))

    except Exception as e:
        logger.info(e)

    finally:
        db_obj.set_db_disconnection()
      

# Python 함수 정의
def my_python_function():
    logger.info("Hello, Airflow!")
    logger.info("Current date: {}".format(datetime.now()))


def display_variable():
    my_var = Variable.get("LOG_DB_URL")
    logger.info('variable' + my_var)
    return my_var


"""
task_env = PythonOperator(task_id='get_variable', python_callable=display_variable, dag=dag)

t1 = BashOperator(
        task_id= 'env_shell',
        bash_command="env.sh",
        dag=dag
)
"""

# PythonOperator
python_delete_alert_task = PythonOperator(
    task_id='prometheus_log_delete_alert_task',
    python_callable=work,
    op_kwargs={"sql": Variable.get("LOG_DELETE_ALERT_SQL"), "_type" : "DELETE"},
    dag=dag,
    provide_context=True
)


# PythonOperator
python_select_alert_task = PythonOperator(
    task_id='prometheus_log_select_alert_task',
    python_callable=work,
    op_kwargs={"sql": Variable.get("LOG_ALERT_SQL"), "_type" : "SELECT"},
    dag=dag,
    provide_context=True
)


# PythonOperator
python_delete_monitoring_log_task = PythonOperator(
    task_id='prometheus_log_delete_monitoring_log_task',
    python_callable=work,
    op_kwargs={"sql": Variable.get("LOG_DELETE_MONITORING_LOG_SQL"), "_type" : "DELETE"},
    dag=dag,
    provide_context=True
)


# PythonOperator
python_select_monitoring_log_task = PythonOperator(
    task_id='prometheus_log_select_monitoring_log_task',
    python_callable=work,
    op_kwargs={"sql": Variable.get("LOG_MONITORING_LOG_SQL"), "_type" : "SELECT"},
    dag=dag,
    provide_context=True
)



# DAG Dependency
python_delete_alert_task >> python_select_alert_task >> python_delete_monitoring_log_task >> python_select_monitoring_log_task
# [python_delete_alert_task, python_delete_monitoring_log_task] >> [python_select_alert_task, python_select_monitoring_log_task]


# DAG Run
if __name__ == "__main__":
    ''' Apache Airflow (or simply Airflow) is a platform to programmatically author, schedule, and monitor workflows. '''
    ''' The advantage of using Airflow over other workflow management tools is that Airflow allows you to schedule and monitor workflows '''
    dag.cli()