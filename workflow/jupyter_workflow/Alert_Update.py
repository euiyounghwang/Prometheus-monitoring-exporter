
import time
import gradio as gr # type: ignore
import requests
import json
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

''' pip install python-dotenv'''
load_dotenv() # will search for .env file in local folder and load variables 

js_func = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""
def get_mail_configuration(es_http_host):
    ''' interface es_config_api http://localhost:8004/config/get_mail_config '''
    try:
        resp = requests.get(url="http://{}:8004/config/get_mail_config".format(es_http_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logging.error(f"es_config_interface api do not reachable")
            return None

        # logging.info(f"get_mail_config - {resp}, {resp.json()}")
        return resp.json()
        

    except Exception as e:
        logging.error(e)
        pass


def transform_to_dict(env_list):
    ''' Transform list to dict'''
    # ['localhost:host1', 'localhost1:host2']
    env_dict = {}
    for element in env_list:
        key_value_pairs = element.split(":")
        env_dict.update({key_value_pairs[0] : key_value_pairs[1]})
    return env_dict


resp_json = {}

def reload_json():
    ''' mail config'''
    # time.sleep(1)

    logging.info(f"config requesting..")
    resp_json = get_mail_configuration(os.getenv('API_HOST'))
    # logging.info(resp_json)
    logging.info(f"config received..")

    return resp_json


def run():

    logging.info(f"Starting")
    
    global resp_json

    env_list = os.getenv('PROMETHEUS_HOST').split(",")
    all_env_dicts = transform_to_dict(env_list)
    
    # resp_json = reload_json()
    
    '''  main gradio run func'''
    def sentence_builder(quantity, animal, countries, place, activity_list, morning, chk):
        return f"""[{chk}] The {quantity} {animal}s from {" and ".join(countries)} went to the {place} where they {" and ".join(activity_list)} until the {"morning" if morning else "night"}"""

    with gr.Blocks(js=js_func) as alert_gradio:
        # resp_json = gr.State({})
        
        ''' main gr.Block'''
        gr.Markdown(f"# Alert Update for Smart Suit Environments on ES Team <a href='{os.getenv('GRAFANA_DASHBOARD_URL')}'>Monitoring</a> Apps!")
        
        def alert_on_off(env):
            ''' check alert for the particular env'''            
            # logging.info(json.dumps(resp_json[all_env_dicts.get(env)], indent=2))
            # return True
            resp_json = reload_json()

            if resp_json[all_env_dicts.get(env)]["is_mailing"]:
                logging.info(f"alert : {True}")
                return {"alert" : True}
            else:
                logging.info(f"alert : {False}")
                return {"alert" : False}
        
        """
        def radio_alert_on_off(env):
            ''' check alert for the particular env'''            
            # resp_json = reload_json()
            
            alert_status = resp_json[all_env_dicts.get(env)]["is_mailing"]
            if alert_status:
                return "On"
            else:
                return "Off"
        """
        
        def alert_radio_on_off(checkbox, radio_button, env):
            logging.info(f'{checkbox} alert_radio_on_off function call..')

            try:
                # will_update_alert = False
                if radio_button == "Off":
                    # return False, False
                    will_update_alert = "false"
                else:
                    # return True, True
                    will_update_alert = "true"
                
                ''' call to DB interface RestAPI'''
                request_body = {
                                "env" : env,
                                "alert" : will_update_alert,
                                "message": "Security Patching"
                }

                logging.info(f"request_body : {request_body}")
                http_urls = "http://{}:8004/config/update_alert_config".format(os.getenv('API_HOST'))
                resp = requests.post(url=http_urls, json=request_body, timeout=600)
                        
                if not (resp.status_code == 200):
                    logging.info(f"alert_radio_on_off in 404 response - {e}")
                    return None, None
                
                logging.info(f"alert update - {resp}")
                # gr.update()

                # reload_json()

                if radio_button == "Off":
                    checkbox = False
                    radio_button = "Off"
                    return False, resp.json()
                else:
                    checkbox = True
                    radio_button = "On"
                    return True, resp.json()
                
            except Exception as e:
                logging.error(e)
                
        with gr.Blocks(js=js_func):
            '''
            with gr.Blocks() as demo:
                val = gr.Textbox()
                for i in range(5):
                    btn = gr.Button(f"Button {i}")
                    btn.click(lambda :random.random(), None, val)
            '''
            with gr.Tab("Dev/Smoke Smart Suite Environment"):
                with gr.Row():
                    '''
                    dev_chk = gr.Checkbox(label="Dev", value=alert_on_off('dev'), info="Alert Status", interactive=False)
                    dev_chk = gr.Checkbox(label="Dev", info="Alert Status", interactive=False)
                    '''
                    dev_chk = gr.Checkbox(label="Dev", value=False, info="Alert Status", interactive=False)
                    dev_radio = gr.Radio(["On", "Off"], value="Off", label="Dev Alert Status", info="Will update this value if you select and click 'Alert Update' btn!")
                    dev_result = gr.Textbox(label="Output")
                    dev_desc = gr.Textbox(label="env", visible=False, value='dev')
                    # dev_desc.change(welcome, inp, out)

                    with gr.Column():
                        ''' Alert Refresh'''
                        update_alert_dev_btn = gr.Button("Alert Refresh")   
                        update_alert_dev_btn.click(fn=alert_on_off, inputs=[dev_desc], outputs=[dev_result], api_name="alert")

                        ''' Alert Update'''
                        update_dev_btn = gr.Button("Alert Update")   
                        # update_dev_btn.click(fn=alert_radio_on_off, inputs=[dev_chk, dev_radio], outputs=[dev_chk, dev_result], api_name="alert")
                        update_dev_btn.click(fn=lambda: gr.update(interactive=False), inputs=None, outputs=update_dev_btn).then(fn=alert_radio_on_off, inputs=[dev_chk, dev_radio, dev_desc], outputs=[dev_result]).then(fn=lambda: gr.update(interactive=True), inputs=None, outputs=update_dev_btn)
                

                with gr.Row():
                    smoke_chk = gr.Checkbox(label="SMOKE", value=False, info="Alert Status", interactive=False)
                    '''
                    smoke_chk = gr.Checkbox(label="SMOKE", info="Alert Status", interactive=False)
                    smoke_radio = gr.Radio(["On", "Off"], label="SMOKE Alert Status", value=radio_alert_on_off('smoke'), info="Will update this value if you select and click 'Alert Update' btn!")
                    '''
                    smoke_radio = gr.Radio(["On", "Off"], value="Off", label="SMOKE Alert Status", info="Will update this value if you select and click 'Alert Update' btn!")
                    smoke_result = gr.Textbox(label="Output")
                    smoke_desc = gr.Textbox(label="env", visible=False, value='smoke')
                
                    with gr.Column():
                        ''' Alert Refresh'''
                        update_alert_smoke_btn = gr.Button("Alert Refresh")   
                        update_alert_smoke_btn.click(fn=alert_on_off, inputs=[smoke_desc], outputs=[smoke_result], api_name="alert")

                        ''' Alert Update'''
                        update_smoke_btn = gr.Button("Alert Update")   
                        update_smoke_btn.click(fn=alert_radio_on_off, inputs=[smoke_chk, smoke_radio, smoke_desc], outputs=[smoke_result], api_name="alert")
                        '''
                        update_smoke_btn.click(fn=alert_radio_on_off, inputs=[smoke_chk, smoke_radio, smoke_desc], outputs=[smoke_chk, smoke_result], api_name="alert")
                        '''
            
            '''
            with gr.Tab("QA Smart Suit Environment"):
                with gr.Row():
                    qa1_chk = gr.Checkbox(label="QA1", value=alert_on_off('qa1'), info="Alert Status", interactive=False)
                    qa1_radio = gr.Radio(["On", "Off"], label="Alert Status", value=radio_alert_on_off('qa1'), info="Will update this value if you select and click 'Alert Update' btn!")
                    qa1_result = gr.Textbox(label="Output")
                    qa1_desc = gr.Textbox(label="env", visible=False, value='qa1')
                    
                update_qa1_btn = gr.Button("Alert Update")   
                update_qa1_btn.click(fn=alert_radio_on_off, inputs=[qa1_chk, qa1_radio, qa1_desc], outputs=[qa1_chk, qa1_result], api_name="alert")
            '''
            with gr.Tab("QA Smart Suite Environment"):
                with gr.Row():
                    qa_list = os.getenv('QA_LIST').split(",")
                    for i in range(len(qa_list)):
                        chk = gr.Checkbox(label=qa_list[i], value=False, info="Alert Status", interactive=False)
                        radio = gr.Radio(["On", "Off"], value="Off", label="{} Alert Status".format(qa_list[i]), info="Will update this value if you select and click 'Alert Update' btn!")
                        result = gr.Textbox(label="Output")
                        desc = gr.Textbox(label="env", visible=False, value='{}'.format(qa_list[i].lower()))

                        with gr.Column():
                            ''' Alert Refresh'''
                            refresh_btn = gr.Button("Alert Refresh")   
                            refresh_btn.click(fn=alert_on_off, inputs=[desc], outputs=[result], api_name="alert")

                            ''' Alert Update'''
                            alert_btn = gr.Button("Alert Update")   
                            alert_btn.click(fn=alert_radio_on_off, inputs=[chk, radio, desc], outputs=[result], api_name="alert")

            '''
            with gr.Tab("Prod Smart Suit Environment"):
                with gr.Row():
                    prod1_chk = gr.Checkbox(label="PROD1", value=alert_on_off('prod1'), info="Alert Status", interactive=False)
                    prod1_radio = gr.Radio(["On", "Off"], label="Alert Status", value=radio_alert_on_off('prod1'), info="Will update this value if you select and click 'Alert Update' btn!")
                    prod1_result = gr.Textbox(label="Output")
                    prod1_desc = gr.Textbox(label="env", visible=False, value='prod1')
                    
                update_prod1_btn = gr.Button("Alert Update")   
                update_prod1_btn.click(fn=alert_radio_on_off, inputs=[prod1_chk, prod1_radio, prod1_desc], outputs=[prod1_chk, prod1_result], api_name="alert")
            '''

            with gr.Tab("Prod Smart Suite Environment"):
                with gr.Row():
                    prod_list = os.environ['PROD_LIST'].split(",")
                    for i in range(len(prod_list)):
                        prod_name = prod_list[i].split(":")
                        chk = gr.Checkbox(label="{} [{}]".format(prod_name[0], prod_name[1]), value=False, info="Alert Status", interactive=False)
                        radio = gr.Radio(["On", "Off"], value="Off", label="{} Alert Status".format(prod_name[0]), info="Will update this value if you select and click 'Alert Update' btn!")
                        result = gr.Textbox(label="Output")
                        desc = gr.Textbox(label="env", visible=False, value='{}'.format(prod_name[0].lower()))

                        with gr.Column():
                            ''' Alert Refresh'''
                            refresh_btn = gr.Button("Alert Refresh")   
                            refresh_btn.click(fn=alert_on_off, inputs=[desc], outputs=[result], api_name="alert")

                            ''' Alert Update'''
                            alert_btn = gr.Button("Alert Update")   
                            alert_btn.click(fn=alert_radio_on_off, inputs=[chk, radio, desc], outputs=[result], api_name="alert")

            ''' Commmand Documentation'''
            with gr.Tab("Scheduled by Cronjob"):
                with gr.Column():
                    gr.Markdown(f"# Will update alert directly via command or add cronjob!")
                    gr.Markdown(f"* Go to Logstash Instance({os.getenv('API_HOST')}) on Dev and will update the alert if you run this command")
                    gr.Markdown(f"* Enable Alert (example) → '/home/{os.getenv('USER')}/es_config_interface/scripts/alert_job_batch.sh {os.getenv('API_HOST')} qa13,qa14 True'")
                    gr.Markdown(f"* Disable Alert (example) → '/home/{os.getenv('USER')}/es_config_interface/scripts/alert_job_batch.sh {os.getenv('API_HOST')} qa13,qa14 false'")
                    gr.Markdown(f"* If you want to add new cronjob for the security patching..")
                    gr.Markdown(f"* sudo crontab -e")
                    gr.Markdown(f"* 40 06 17 12 *  /home/{os.getenv('USER')}/es_config_interface/scripts/alert_job_batch.sh {os.getenv('API_HOST')} qa1 false")
                    gr.Markdown(f"* 00 16 17 12 *  /home/{os.getenv('USER')}/es_config_interface/scripts/alert_job_batch.sh {os.getenv('API_HOST')} qa1 true")
                    gr.Markdown(f"* 40 06 17 12 *  /home/{os.getenv('USER')}/es_config_interface/scripts/alert_job_batch.sh {os.getenv('API_HOST')} qa13,qa14 false")
                    gr.Markdown(f"* 00 16 17 12 *  /home/{os.getenv('USER')}/es_config_interface/scripts/alert_job_batch.sh {os.getenv('API_HOST')} qa13,qa14 true")
                         

    alert_gradio.launch(auth = (os.getenv('GRADIO_USER'),os.getenv('GRADIO_PASSWORD')), server_name="0.0.0.0", server_port=7090)


if __name__ == '__main__':
    ''' reference : https://www.gradio.app/docs/gradio/checkbox'''
    ''' gradio ./workflow/jupyter_workflow/Alert_Update.py'''
    ''' ./workflow/jupyter_workflow/alert-update-start.sh '''
    run()