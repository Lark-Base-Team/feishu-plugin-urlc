from rembg import remove, new_session
from PIL import Image
import time

model_name = "u2netp"
session = new_session(model_name)

def remove_image_bg(file: str):
    start_time = time.time()

    input_path = file
    output_path = 'output.png'

    input = Image.open(input_path)
    output = remove(input, session=session)
    output.save(output_path)

    # Your function call goes here

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

if __name__ == '__main__':
    remove_image_bg('/home/ubuntu/projects/liujun/feishu-plugin-rembg/92aee9d71af628254775432f7410e015.jpg')