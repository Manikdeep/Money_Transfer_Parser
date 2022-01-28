import os
import sys
from google.cloud import vision
import io

"""check names before checking most dominant colors
ie if it says paypal there is no need to check if there is blue. 
for cashapp, check if there is a username ($CashappName) before 
checking for the green color"""

def get_image_paths(folder):
    re = []
    for filename in os.listdir(folder):
        re.append(os.path.join(folder, filename))
    return re

def detect_properties(path, img_file_path):
    """Detects image properties in the file."""
    """if the green is greater than red and blue, it is cashapp. """
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    test = vision.ImageAnnotatorClient.annotate_image
    response = client.image_properties(image=image)
    props = response.image_properties_annotation
    #print('Properties:')
    colors_doc = ""
    colors_dict = {}
    pic_id = path[-34:-4]
    print(pic_id)
    for color in props.dominant_colors.colors:
        """colors_doc += 'fraction: {}'.format(color.pixel_fraction) + '\n'
        colors_doc += '\tr: {}'.format(color.color.red) + '\n'
        colors_doc += '\tg: {}'.format(color.color.green) + '\n'
        colors_doc += '\tb: {}'.format(color.color.blue) + '\n'
        colors_doc += '\ta: {}'.format(color.color.alpha) + '\n'"""
        if pic_id not in colors_dict:
            colors_dict[pic_id] = []
        colors_dict[pic_id].append(color.pixel_fraction)
        colors_dict[pic_id].append(('r', color.color.red))
        colors_dict[pic_id].append(('g', color.color.green))
        colors_dict[pic_id].append(('b', color.color.blue))
    """file_name = os.path.basename(path).split(".")[0]
    with open(img_file_path+file_name+'.txt','w', encoding='utf-8') as f:
         f.write(colors_doc) """       
    return colors_dict

def detect_text(path, text_file_path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    #response = client.text_detection(image=image)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    text_doc = ""
    
    for text in texts:        
        text_doc += text.description + " "
    file_name = os.path.basename(path).split(".")[0]
    with open(text_file_path+file_name+'.txt','w', encoding='utf-8') as f:
         f.write(text_doc)        
    return text_doc
    
if __name__ == '__main__':
    folder_images_path = "C:/Users/jonat/OneDrive/Documents/money-transfer-sample-images - Copy"
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/jonat/GoogleAPIParserKey"
    img_paths = get_image_paths(folder_images_path)
    dirs = folder_images_path.split("/")
    print(dirs)
    get_root_dir_img = "/".join([dirs[i] for i in range(0,len(dirs)-1)])
    print(get_root_dir_img)
    #os.mkdir(get_root_dir_img+"/money_text")
    directory = "money_text"
    parent_dir = "C:/Users/jonat/OneDrive/Documents/VisualStudioRepositories/Money_Transfer_Parser"
    path = os.path.join(parent_dir, directory)
    #if not os.path.exists(get_root_dir_img+"/checks_text"):
    #    os.makedirs(get_root_dir_img+"/checks_text")
    if not os.path.exists(path):
        os.makedirs(path)
    for img_path in img_paths: 
        #detect_text(img_path, get_root_dir_img+"/checks_text/")
        print(detect_properties(img_path, path))
        #print(path)