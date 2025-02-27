import gradio as gr
import os

'''
def foo(dir):
    return [d.name for d in dir]

with gr.Blocks() as demo:
    # input = gr.File(file_count="directory")
    # path = 'C://Users/test/Downloads/scripts/'
    files_list = os.listdir('C://Users/test/Downloads/scripts/')
    # gr.inputs.File(file_count=path)
    files = gr.Textbox()
    show = gr.Button(value="Show")
    # show.click(foo, input, files)
    show.click(None, inputs=files_list, outputs=files)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7010)
'''


'''
WebCam..

import gradio as gr
import numpy as np
from PIL import Image

with gr.Blocks(css="footer{display:none !important}", fill_width=True) as webui:
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type='filepath', height=512)
            file_name = gr.TextArea(lines=1, show_label=False)
        with gr.Column():
            image_output = gr.Image(height=512)
    def output_image(img_fileobj):
        pilImage = Image.open(img_fileobj)
        numpyImage = np.array(pilImage)
        filename = img_fileobj
        return [numpyImage, filename]
    image_input.change(
        output_image,
        inputs=[image_input],
        outputs=[image_output, file_name]
    )

if __name__ == "__main__":
    webui.launch(server_name="0.0.0.0", server_port=7010)
'''

import gradio as gr

with gr.Blocks() as demo:
    gr.FileExplorer(file_count="multiple", ignore_glob="*.db",
                    interactive=True, glob="**/*.*")

demo.launch(server_name="0.0.0.0", server_port=7010)


