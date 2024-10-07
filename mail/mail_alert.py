import subprocess
import os
import re

# Function that send email.
def send_mail(body, env, status, to):
    ''' send mail through mailx based on python environment'''
    if not body:
        return
    grafana_dashboard_url = os.environ["GRAFANA_DASHBOARD_URL"]
    
    """
    body = "Monitoring [ES Team Dashboard on export application]'\n\t' \
        - Grafana Dashboard URL : {}'\n\t' \
        - Enviroment: {}'\n\t' \
        - Status: {}'\n\t' \
        - Alert Message : {} \
        ".format(grafana_dashboard_url, env, status, body)
    """
    body = "test"

    email_user_list = to.split(",")
    print(f"email_user_list : {email_user_list}")
    """
    for user in email_user_list:
        print(user)
        cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert' " + "-c a@test.mail " + to
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, errors = result.communicate()
        if output:
            print(f"Send mail to user : {user}, output : {output}")
        if errors:
            print(errors)
    """

    # cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert' " + "-c a@test.mail " + to
    # cmd=f"echo {body} | mailx -r a@xyz.com -s 'Prometheus Monitoring Alert' " + "-c ea@xyz.com " + to
    cmd=f"echo {body} | mailx -s 'Prometheus Monitoring Alert' " + "-c a@xyz.com " + "1@txt.att.net"
    print(f"# {cmd}")

    try:
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, errors = result.communicate()
        if output:
            print(f"Send mail output : {output}")
        if errors:
            print(errors)
    except Exception as e:
        print(e)
    

if __name__ == '__main__':
    # Send Email
    body_text = "org.apache.kafka.connect.errors.ConnectException: java.sql.SQLRecoverableException: IO Error: The Network Adapter could not establish the connection\n\tat io.confluent.connect.jdbc.util.CachedConnectionProvider.getValidConnection(CachedConnectionProvider.java:70)\n\tat io.confluent.connect.jdbc.source.JdbcSourceTask.poll(JdbcSourceTask.java:203)\n\tat org.apache.kafka.connect.runtime.WorkerSourceTask.execute(WorkerSourceTask.java:163)\n\tat org.apache.kafka.connect.runtime.WorkerTask.doRun(WorkerTask.java:146)\n\tat org.apache.kafka.connect.runtime.WorkerTask.run(WorkerTask.java:190)\n\tat java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)\n\tat java.util.concurrent.FutureTask.run(FutureTask.java:266)\n\tat java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)\n\tat java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)\n\tat java.lang.Thread.run(Thread.java:748)\nCaused by: java.sql.SQLRecoverableException: IO Error: The Network Adapter could not establish the connection\n\tat oracle.jdbc.driver.T4CConnection.logon(T4CConnection.java:673)\n\tat oracle.jdbc.driver.PhysicalConnection.<init>(PhysicalConnection.java:715)\n\tat oracle.jdbc.driver.T4CConnection.<init>(T4CConnection.java:385)\n\tat "
    body_text = body_text.replace('\n\t', " ").replace('\n', " ")
    body_text = re.sub(r"[^\uAC00-\uD7A30-9a-zA-Z\s]", "", body_text)
    print("str - ", body_text)
    email_list = os.environ["EMAIL_LIST"]
    print(f"mail_list : {email_list}")
    ''' Call function to send an email'''
    for user in email_list.split(","):
        send_mail(body=body_text, env='Dev', status='Yellow', to=email_list)
    # send_mail(body=body_text, env='Dev', status='Yellow', to=email_list)