import os
from google.cloud import vision
import io

# check names before checking most dominant colors
# ie if it says paypal there is no need to check if there is blue. 
# for cashapp, check if there is a username ($CashappName) before 
# checking for the green color
colors_dict = {}
def get_image_paths(folder):
    """Gets path of images folder"""
    re = []
    for filename in os.listdir(folder):
        re.append(os.path.join(folder, filename))
    return re

def detect_properties(path):
    """Detects image properties in the file."""
    # if the green is greater than red and blue, it is cashapp.
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    test = vision.ImageAnnotatorClient.annotate_image
    response = client.image_properties(image=image)
    props = response.image_properties_annotation
    photo = path[path.index('\\'):]
    id = photo[photo.index('_')+1: photo.index('@')]
    pic_id = int(id)
    print("getting color properties for ", pic_id)
    for color in props.dominant_colors.colors:
        if pic_id not in colors_dict:
            colors_dict[pic_id] = []
        colors_dict[pic_id].append(color.pixel_fraction)
        colors_dict[pic_id].append(color.color.red)
        colors_dict[pic_id].append(color.color.green)
        colors_dict[pic_id].append(color.color.blue)  
    return colors_dict

# def detect_text(path, text_file_path):
def detect_text(path):
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
    # with open(text_file_path+file_name+'.txt','w', encoding='utf-8') as f:
    #      f.write(text_doc)  
    print(text_doc)      
    return text_doc
   
# Update the following path with the correct path of the photos on your system
folder_images_path = "C:/Users/jonat/Downloads/Photos (2)/Photos"
# folder_images_path = "C:/Users/jonat/OneDrive/Documents/French Pictures"
img_paths = get_image_paths(folder_images_path)
dirs = folder_images_path.split("/")
get_root_dir_img = "/".join([dirs[i] for i in range(0,len(dirs)-1)])

directory = "money_text"
parent_dir = "C:/Users/jonat/OneDrive/Documents/VisualStudioRepositories/Money_Transfer_Parser"
path = os.path.join(parent_dir, directory)

for img_path in img_paths:
    # Get color information from pictures
    detect_properties(img_path)
# print(colors_dict)
