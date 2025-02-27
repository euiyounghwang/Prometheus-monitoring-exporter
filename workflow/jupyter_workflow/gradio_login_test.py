
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

USERNAME = 'a'
PASSWORD = 'a'

def authenticate(username, password):
    if username == USERNAME and password == PASSWORD:
        return True
        
    else:
        return False
    
def greet(name):
    return "Hello " + name + "!!"


def run():
    logging.info(f"Starting")
    
    iface = gr.Interface(fn=greet, inputs="text", outputs="text")
    iface.launch(auth = (os.getenv('GRADIO_USER'),os.getenv('GRADIO_PASSWORD')), auth_message= "🦄 Alert Update User Interface for The ES Team", server_name="0.0.0.0", server_port=7010)
    # iface.launch(auth = authenticate, auth_message= "🦄 Alert Update User Interface for The ES Team", server_name="0.0.0.0", server_port=7010)
    
  
if __name__ == '__main__':
    ''' reference : https://www.gradio.app/docs/gradio/checkbox'''
    ''' gradio ./workflow/jupyter_workflow/Alert_Update.py'''
    ''' ./workflow/jupyter_workflow/alert-update-start.sh '''
    ''' Auth : https://wooiljeong.github.io/etc/intro-gradio/'''
    run()