import streamlit as st
import time
import requests, socket
import logging
import os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

st.set_page_config(page_title='ES Team Alert Monitoring! 👋', layout = 'wide', page_icon = 'logo2.png', initial_sidebar_state = 'auto')
p = st.empty()
p.title('ES Team Alert Monitoring! 👋')

# envs = ['Dev', 'Smoke', 'Prod1']

# for i in envs:
#     i = st.empty()
#     i.subheader('Dev')  

dev = st.empty()
dev.subheader('Dev')  
dev = st.empty()

smoke = st.empty()
smoke.subheader('Smoke')  
smoke = st.empty()

prod1 = st.empty()
prod1.subheader('Prod1')  
prod1 = st.empty()

prod2 = st.empty()
prod2.subheader('Prod2')  
prod2 = st.empty()

prod3 = st.empty()
prod3.subheader('Prod3')  
prod3 = st.empty()

prod4 = st.empty()
prod4.subheader('Prod4')  
prod4 = st.empty()

prod6 = st.empty()
prod6.subheader('Prod6')  
prod6 = st.empty()

prod7 = st.empty()
prod7.subheader('Prod7')  
prod7 = st.empty()

prod8 = st.empty()
prod8.subheader('Prod8')  
prod8 = st.empty()

prod9 = st.empty()
prod9.subheader('Prod9')  
prod9 = st.empty()

prod10 = st.empty()
prod10.subheader('Prod10')  
prod10 = st.empty()

prod12 = st.empty()
prod12.subheader('Prod12')  
prod12 = st.empty()

prod13 = st.empty()
prod13.subheader('Prod13')  
prod13 = st.empty()

prod14 = st.empty()
prod14.subheader('Prod14')  
prod14 = st.empty()

prod16 = st.empty()
prod16.subheader('Prod16')  
prod16 = st.empty()

prod17 = st.empty()
prod17.subheader('Prod17')  
prod17 = st.empty()

prod18 = st.empty()
prod18.subheader('Prod18')  
prod18 = st.empty()

prod19 = st.empty()
prod19.subheader('Prod19')  
prod19 = st.empty()

prod20 = st.empty()
prod20.subheader('Prod20')  
prod20 = st.empty()

qa1 = st.empty()
qa1.subheader('Qa1')  
qa1 = st.empty()

qa2 = st.empty()
qa2.subheader('Qa2')  
qa2 = st.empty()

qa4 = st.empty()
qa4.subheader('Qa4')  
qa4 = st.empty()

qa6 = st.empty()
qa6.subheader('Qa6')  
qa6 = st.empty()

qa9 = st.empty()
qa9.subheader('Qa9')  
qa9 = st.empty()

qa11 = st.empty()
qa11.subheader('Qa11')  
qa11 = st.empty()

qa13 = st.empty()
qa13.subheader('Qa13')  
qa13 = st.empty()

qa13_new = st.empty()
qa13_new.subheader('Qa13_new')  
qa13_new = st.empty()

qa14 = st.empty()
qa14.subheader('Qa14')  
qa14 = st.empty()

qa15 = st.empty()
qa15.subheader('Qa15')  
qa15 = st.empty()

qa16 = st.empty()
qa16.subheader('Qa16')  
qa16 = st.empty()

qa17 = st.empty()
qa17.subheader('Qa17')  
qa17 = st.empty()

qa18 = st.empty()
qa18.subheader('Qa18')  
qa18 = st.empty()

qa20 = st.empty()
qa20.subheader('Qa20')  
qa20 = st.empty()

qa22 = st.empty()
qa22.subheader('Qa22')  
qa22 = st.empty()

qa25 = st.empty()
qa25.subheader('Qa25')  
qa25 = st.empty()

qa26 = st.empty()
qa26.subheader('Qa26')  
qa26 = st.empty()

def get_mail_configuration(db_http_host):
    ''' interface es_config_api http://localhost:8004/config/get_mail_config '''
    try:
        es_config_host = str(db_http_host).split(":")[0]
        # logging.info(f"es_config_host : {es_config_host}")
        resp = requests.get(url="http://{}:8004/config/get_mail_config".format(es_config_host), timeout=5)
                
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



def Display(resp, all_env_dicts):
    ''' Display'''
    
    # ''' dev '''
    if resp[all_env_dicts.get("dev")]["is_mailing"]:
        dev.success(f'Alert {resp[all_env_dicts.get("dev")]["is_mailing"]}')
    else:
        dev.error(f'Alert {resp[all_env_dicts.get("dev")]["is_mailing"]}')

    # ''' smoke '''
    if resp[all_env_dicts.get("smoke")]["is_mailing"]:
        smoke.success(f'Alert {resp[all_env_dicts.get("smoke")]["is_mailing"]}')
    else:
        smoke.error(f'Alert {resp[all_env_dicts.get("smoke")]["is_mailing"]}')

    # ''' prod1 '''
    if resp[all_env_dicts.get("prod1")]["is_mailing"]:
        prod1.success(f'Alert {resp[all_env_dicts.get("prod1")]["is_mailing"]}')
    else:
        prod1.error(f'Alert {resp[all_env_dicts.get("prod1")]["is_mailing"]}')

    # ''' prod2 '''
    if resp[all_env_dicts.get("prod2")]["is_mailing"]:
        prod2.success(f'Alert {resp[all_env_dicts.get("prod2")]["is_mailing"]}')
    else:
        prod2.error(f'Alert {resp[all_env_dicts.get("prod2")]["is_mailing"]}')

    # ''' prod3 '''
    if resp[all_env_dicts.get("prod3")]["is_mailing"]:
        prod3.success(f'Alert {resp[all_env_dicts.get("prod3")]["is_mailing"]}')
    else:
        prod3.error(f'Alert {resp[all_env_dicts.get("prod3")]["is_mailing"]}')

    # ''' prod4 '''
    if resp[all_env_dicts.get("prod4")]["is_mailing"]:
        prod4.success(f'Alert {resp[all_env_dicts.get("prod4")]["is_mailing"]}')
    else:
        prod4.error(f'Alert {resp[all_env_dicts.get("prod4")]["is_mailing"]}')

    # ''' prod6 '''
    if resp[all_env_dicts.get("prod6")]["is_mailing"]:
        prod6.success(f'Alert {resp[all_env_dicts.get("prod6")]["is_mailing"]}')
    else:
        prod6.error(f'Alert {resp[all_env_dicts.get("prod6")]["is_mailing"]}')

    # ''' prod7 '''
    if resp[all_env_dicts.get("prod7")]["is_mailing"]:
        prod7.success(f'Alert {resp[all_env_dicts.get("prod7")]["is_mailing"]}')
    else:
        prod7.error(f'Alert {resp[all_env_dicts.get("prod7")]["is_mailing"]}')

    # ''' prod8 '''
    if resp[all_env_dicts.get("prod8")]["is_mailing"]:
        prod8.success(f'Alert {resp[all_env_dicts.get("prod8")]["is_mailing"]}')
    else:
        prod8.error(f'Alert {resp[all_env_dicts.get("prod8")]["is_mailing"]}')

    # ''' prod9 '''
    if resp[all_env_dicts.get("prod9")]["is_mailing"]:
        prod9.success(f'Alert {resp[all_env_dicts.get("prod9")]["is_mailing"]}')
    else:
        prod9.error(f'Alert {resp[all_env_dicts.get("prod9")]["is_mailing"]}')

     # ''' prod10 '''
    if resp[all_env_dicts.get("prod10")]["is_mailing"]:
        prod10.success(f'Alert {resp[all_env_dicts.get("prod10")]["is_mailing"]}')
    else:
        prod10.error(f'Alert {resp[all_env_dicts.get("prod10")]["is_mailing"]}')

    # ''' prod12 '''
    if resp[all_env_dicts.get("prod12")]["is_mailing"]:
        prod12.success(f'Alert {resp[all_env_dicts.get("prod12")]["is_mailing"]}')
    else:
        prod12.error(f'Alert {resp[all_env_dicts.get("prod12")]["is_mailing"]}')

    # ''' prod13 '''
    if resp[all_env_dicts.get("prod13")]["is_mailing"]:
        prod13.success(f'Alert {resp[all_env_dicts.get("prod13")]["is_mailing"]}')
    else:
        prod13.error(f'Alert {resp[all_env_dicts.get("prod13")]["is_mailing"]}')

    # ''' prod14 '''
    if resp[all_env_dicts.get("prod14")]["is_mailing"]:
        prod14.success(f'Alert {resp[all_env_dicts.get("prod14")]["is_mailing"]}')
    else:
        prod14.error(f'Alert {resp[all_env_dicts.get("prod14")]["is_mailing"]}')

    # ''' prod16 '''
    if resp[all_env_dicts.get("prod16")]["is_mailing"]:
        prod16.success(f'Alert {resp[all_env_dicts.get("prod16")]["is_mailing"]}')
    else:
        prod16.error(f'Alert {resp[all_env_dicts.get("prod16")]["is_mailing"]}')

    # ''' prod17 '''
    if resp[all_env_dicts.get("prod17")]["is_mailing"]:
        prod17.success(f'Alert {resp[all_env_dicts.get("prod17")]["is_mailing"]}')
    else:
        prod17.error(f'Alert {resp[all_env_dicts.get("prod17")]["is_mailing"]}')

    # ''' prod18 '''
    if resp[all_env_dicts.get("prod18")]["is_mailing"]:
        prod18.success(f'Alert {resp[all_env_dicts.get("prod18")]["is_mailing"]}')
    else:
        prod18.error(f'Alert {resp[all_env_dicts.get("prod18")]["is_mailing"]}')

    # ''' prod19 '''
    if resp[all_env_dicts.get("prod19")]["is_mailing"]:
        prod19.success(f'Alert {resp[all_env_dicts.get("prod19")]["is_mailing"]}')
    else:
        prod19.error(f'Alert {resp[all_env_dicts.get("prod19")]["is_mailing"]}')

    # ''' prod20 '''
    if resp[all_env_dicts.get("prod20")]["is_mailing"]:
        prod20.success(f'Alert {resp[all_env_dicts.get("prod20")]["is_mailing"]}')
    else:
        prod20.error(f'Alert {resp[all_env_dicts.get("prod20")]["is_mailing"]}')

    # ''' qa1 '''
    if resp[all_env_dicts.get("qa1")]["is_mailing"]:
        qa1.success(f'Alert {resp[all_env_dicts.get("qa1")]["is_mailing"]}')
    else:
        qa1.error(f'Alert {resp[all_env_dicts.get("qa1")]["is_mailing"]}')

    # ''' qa2 '''
    if resp[all_env_dicts.get("qa2")]["is_mailing"]:
        qa2.success(f'Alert {resp[all_env_dicts.get("qa2")]["is_mailing"]}')
    else:
        qa2.error(f'Alert {resp[all_env_dicts.get("qa2")]["is_mailing"]}')

    # ''' qa4 '''
    if resp[all_env_dicts.get("qa4")]["is_mailing"]:
        qa4.success(f'Alert {resp[all_env_dicts.get("qa4")]["is_mailing"]}')
    else:
        qa4.error(f'Alert {resp[all_env_dicts.get("qa4")]["is_mailing"]}')

    # ''' qa6 '''
    if resp[all_env_dicts.get("qa6")]["is_mailing"]:
        qa6.success(f'Alert {resp[all_env_dicts.get("qa6")]["is_mailing"]}')
    else:
        qa6.error(f'Alert {resp[all_env_dicts.get("qa6")]["is_mailing"]}')

    # ''' qa9 '''
    if resp[all_env_dicts.get("qa9")]["is_mailing"]:
        qa9.success(f'Alert {resp[all_env_dicts.get("qa9")]["is_mailing"]}')
    else:
        qa9.error(f'Alert {resp[all_env_dicts.get("qa9")]["is_mailing"]}')
    
    # ''' qa11 '''
    if resp[all_env_dicts.get("qa11")]["is_mailing"]:
        qa11.success(f'Alert {resp[all_env_dicts.get("qa11")]["is_mailing"]}')
    else:
        qa11.error(f'Alert {resp[all_env_dicts.get("qa11")]["is_mailing"]}')

    # ''' qa13 '''
    if resp[all_env_dicts.get("qa13")]["is_mailing"]:
        qa13.success(f'Alert {resp[all_env_dicts.get("qa13")]["is_mailing"]}')
    else:
        qa13.error(f'Alert {resp[all_env_dicts.get("qa13")]["is_mailing"]}')

    # ''' qa13_new '''
    if resp[all_env_dicts.get("qa13_new")]["is_mailing"]:
        qa13_new.success(f'Alert {resp[all_env_dicts.get("qa13_new")]["is_mailing"]}')
    else:
        qa13_new.error(f'Alert {resp[all_env_dicts.get("qa13_new")]["is_mailing"]}')

    # ''' qa14 '''
    if resp[all_env_dicts.get("qa14")]["is_mailing"]:
        qa14.success(f'Alert {resp[all_env_dicts.get("qa14")]["is_mailing"]}')
    else:
        qa14.error(f'Alert {resp[all_env_dicts.get("qa14")]["is_mailing"]}')

    # ''' qa15 '''
    if resp[all_env_dicts.get("qa15")]["is_mailing"]:
        qa15.success(f'Alert {resp[all_env_dicts.get("qa15")]["is_mailing"]}')
    else:
        qa15.error(f'Alert {resp[all_env_dicts.get("qa15")]["is_mailing"]}')

    # ''' qa16 '''
    if resp[all_env_dicts.get("qa16")]["is_mailing"]:
        qa16.success(f'Alert {resp[all_env_dicts.get("qa16")]["is_mailing"]}')
    else:
        qa16.error(f'Alert {resp[all_env_dicts.get("qa16")]["is_mailing"]}')

    # ''' qa17 '''
    if resp[all_env_dicts.get("qa17")]["is_mailing"]:
        qa17.success(f'Alert {resp[all_env_dicts.get("qa17")]["is_mailing"]}')
    else:
        qa17.error(f'Alert {resp[all_env_dicts.get("qa17")]["is_mailing"]}')

    # ''' qa18 '''
    if resp[all_env_dicts.get("qa18")]["is_mailing"]:
        qa18.success(f'Alert {resp[all_env_dicts.get("qa18")]["is_mailing"]}')
    else:
        qa18.error(f'Alert {resp[all_env_dicts.get("qa18")]["is_mailing"]}')

    # ''' qa20 '''
    if resp[all_env_dicts.get("qa20")]["is_mailing"]:
        qa20.success(f'Alert {resp[all_env_dicts.get("qa20")]["is_mailing"]}')
    else:
        qa20.error(f'Alert {resp[all_env_dicts.get("qa20")]["is_mailing"]}')

    # ''' qa22 '''
    if resp[all_env_dicts.get("qa22")]["is_mailing"]:
        qa22.success(f'Alert {resp[all_env_dicts.get("qa22")]["is_mailing"]}')
    else:
        qa22.error(f'Alert {resp[all_env_dicts.get("qa22")]["is_mailing"]}')

    # ''' qa25 '''
    if resp[all_env_dicts.get("qa25")]["is_mailing"]:
        qa25.success(f'Alert {resp[all_env_dicts.get("qa25")]["is_mailing"]}')
    else:
        qa25.error(f'Alert {resp[all_env_dicts.get("qa25")]["is_mailing"]}')

      # ''' qa25 '''
    if resp[all_env_dicts.get("qa26")]["is_mailing"]:
        qa26.success(f'Alert {resp[all_env_dicts.get("qa26")]["is_mailing"]}')
    else:
        qa26.error(f'Alert {resp[all_env_dicts.get("qa26")]["is_mailing"]}')

    # input_user_name = st.text_input(label="User Name", value=f'Alert {resp[all_env_dicts.get("prod3")]["is_mailing"]}')


def work():
    ''' Main work func'''
    # x = 0
    env_list = os.getenv('PROMETHEUS_HOST').split(",")
    all_env_dicts = transform_to_dict(env_list)
    
    while True:
        # ''' get alert results every 5 seconds'''
        resp = get_mail_configuration(os.getenv('API_HOST'))    
        Display(resp, all_env_dicts)
        
        # p.write(f"Your value is {x}")
        # prod1.success(f'Alert  {x}')
        time.sleep(5)



if __name__ == '__main__':
    # ''' streamlit run main.py '''
    work()