import cv2
import pytesseract
from unidecode import unidecode
import numpy as np
import re
from PIL import ImageFont, ImageDraw, Image
import time

def distance(arr1, arr2):
    return np.sqrt(np.sum((arr1 - arr2)**2, axis=1))

def dot_checking(str_):
    return ('....' in str_)

def empty_str_checking(str_):
    return (str_ == '')

def remove_accent_uncapitalize(str):
    return unidecode(str).lower()

def box_merging(results):
    # conf = np.array([int(conf) for conf in results['conf']])
    text = results['text']

    ## Remove empty strings
    text = np.array([empty_str_checking(text_) for text_ in text])
    idx = np.where(text == False)
    left = np.array(results['left'])[idx]
    top = np.array(results['top'])[idx]
    width = np.array(results['width'])[idx]
    height = np.array(results['height'])[idx]
    text = np.array(results['text'])[idx]
    full_text = np.array(results['full_text'])[idx]

    arr1 = np.stack((left, np.add(top, height)), axis=1)
    arr2 = np.stack((np.add(left, width), np.add(top, height)), axis=1)
    dists = distance(arr2[:-1], arr1[1:])
    merge_results = {
        'cluster': [],
        'text': [],
        'full_text': []
    }
    left = left.tolist()
    top = top.tolist()
    width = width.tolist()
    height = height.tolist()
    cont = False
    last_id = 0
    for (id, dist) in enumerate(dists):
        if id == 0:
            merge_results['cluster'].append([left[id], top[id], width[id], height[id]])
            merge_results['text'].append(text[id])
            merge_results['full_text'].append(full_text[id])
        if dist < 150 and dot_checking(text[id+1])==False and dot_checking(text[id])==False:
            tmp = merge_results['cluster'][last_id]
            merge_results['cluster'][last_id][0] = min(tmp[0], left[id+1])
            merge_results['cluster'][last_id][1] = min(tmp[1], top[id+1])
            merge_results['cluster'][last_id][2] = tmp[2]+dist+width[id+1]
            merge_results['cluster'][last_id][3] = max(tmp[3], height[id+1])
            merge_results['text'][last_id] += ' ' + text[id+1]
            merge_results['full_text'][last_id] += ' ' + full_text[id+1]
        else:
            merge_results['cluster'].append([left[id+1], top[id+1], width[id+1], height[id+1]])
            merge_results['text'].append(text[id+1])
            merge_results['full_text'].append(full_text[id+1])
            last_id += 1

    return merge_results

def key_count(threshold, patterns, results):
    key_count_dict = dict.fromkeys(list(patterns.keys()), 0)
    results['key'] = []
    results['similarity'] = []
    for id, text in enumerate(results['text']):
        if len(text) > 35:
            results['key'].append("NULL")
            results['similarity'].append(0)
            continue
        highest_similarity = 0
        highest_similarity_key = "NULL"
        for key in patterns.keys():
            result = process.extractOne(text, patterns[key])
            # result = process.extractOne(text, patterns[key], scorer=fuzz.ratio)
            if result[1] > highest_similarity:
                highest_similarity_key = key
                highest_similarity = result[1]

        if highest_similarity >= threshold:
            if highest_similarity_key not in key_count_dict:
                key_count_dict[highest_similarity_key] = 1
            key_count_dict[highest_similarity_key] += 1

        results['key'].append(highest_similarity_key)
        results['similarity'].append(highest_similarity) 
    return key_count_dict

def recognize_and_put_text_fuzzy(threshold, patterns, data, results, image, font, font_size):
    filled_key_arr = []
    filled_dot_id_arr = []
    last_id = dict()
    key_count_dict = key_count(threshold, patterns, results)
    detected_key_arr = dict.fromkeys(list(patterns.keys()), 0)
    print(list(zip(results['key'], results['similarity'])))

    for id, text in enumerate(results['text']):
        print('-------------------')
        key = results['key'][id]
        similarity = results['similarity'][id]
        print((text, key, similarity))
        if len(text) > 35 or key=="NULL" or similarity < threshold:
            continue

        print("Accepted")
        detected_key_arr[key] += 1
        if key_count_dict[key] > 2:
            if detected_key_arr[key] > 1 and detected_key_arr[key] <= key_count_dict[key]/2:
                continue
        if len(filled_key_arr) > 0 and key == filled_key_arr[-1]:
            continue
        if key in last_id:
            last_id[key] += 1
            if last_id[key] >= len(data[key]):
                continue
        else:
            last_id[key] = 0

        filling_data = data[key][last_id[key]]
        coor = results['cluster'][id]
        nearest_dot_id = id+1
        dot_found = False
        while nearest_dot_id < len(results['text']):
            if dot_checking(results['text'][nearest_dot_id]) == True and (nearest_dot_id not in filled_dot_id_arr):
                dot_found = True
                break
            else:
                nearest_dot_id += 1

        if dot_found == True:
            filled_dot_id_arr.append(nearest_dot_id)
            print(nearest_dot_id)
            print(filled_dot_id_arr)
            print(filling_data)
            filled_key_arr.append(key)
            dot_coor = results['cluster'][nearest_dot_id]
            padding_width = dot_coor[2]*0.2
            x = dot_coor[0] + padding_width
            y = dot_coor[1] + dot_coor[3]
            img_pil = Image.fromarray(image)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x, y - font_size),  filling_data, font = font, fill = (0, 0, 0, 1))
            image = np.array(img_pil)
    return image

def entity_detection(merge_results):
    entity_lst = list()
    id = 0
    name_count = {}
    while id < len(merge_results['text'])-1:
        if len(merge_results['text'][id]) <= 1 or dot_checking(merge_results['text'][id]):
            # print(merge_results['text'][id] + 'rejected')
            id += 1
            continue
        dot_id = id+1
        if len(merge_results['text'][dot_id]) <= 1:
            dot_id += 1
        if dot_checking(merge_results['text'][dot_id]):
            entity_name = re.sub('[^0-9a-zA-Z]+', '_', merge_results['text'][id])
            if entity_name[-1] == '_':
                entity_name = entity_name[:-1]
            if entity_name in name_count:
                name_count[entity_name] += 1
            else:
                name_count[entity_name] = 1
            entity_name += str("_") + str(name_count[entity_name])
            entity_lst.append({
                'name': entity_name,
                'description': merge_results['full_text'][id],
                'bb': merge_results['cluster'][dot_id],
            })
            id = dot_id + 1
        else:
            id += 1
    return entity_lst

def data_filling(input_2, image, font_size, fontpath):
    font = ImageFont.truetype(fontpath, font_size)
    height = image.shape[0]
    width = image.shape[1]
    img_pil = Image.fromarray(image)
    for i, entity in enumerate(input_2):
        try:
            filling_data = entity['data']
            dot_coor = entity['bb']
            dot_coor[0] = dot_coor[0]*width
            dot_coor[1] = dot_coor[1]*height
            dot_coor[2] = dot_coor[2]*width
            dot_coor[3] = dot_coor[3]*height
            padding_width = dot_coor[2]*0.02
            x = dot_coor[0] + padding_width
            y = dot_coor[1] + dot_coor[3]

            # Write on the form
            draw = ImageDraw.Draw(img_pil)
            draw.text((x, y - font_size),  filling_data, font = font, fill = (0, 0, 0, 1))
        except:
            pass
    image = np.array(img_pil)
    return image

def fields_detection(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # OCR the image, supplying the country code as the language parameter
    # options = "-l {} --psm {}".format(args["lang"], args["psm"])
    options = "-l {} --psm {} --oem {}".format("eng+vie", "3", "0")
    results = pytesseract.image_to_data(image_gray, config=options, output_type=pytesseract.Output.DICT)
    results['full_text'] = [text for text in results['text']]
    results['text'] = [remove_accent_uncapitalize(text) for text in results['text']]
    merge_results = box_merging(results)
    entity_lst= entity_detection(merge_results)
    height = image.shape[0]
    width = image.shape[1]
    for entity in entity_lst:
        tmp = []
        tmp.append(entity['bb'][0]/width)
        tmp.append(entity['bb'][1]/height)
        tmp.append(entity['bb'][2]/width)
        tmp.append(entity['bb'][3]/height)
        entity['bb'] = tmp

    id = len(merge_results['text'])//2
    while True:
        if dot_checking(merge_results['text'][id]):
            id += 1
            pass
        else:
            font_size = merge_results['cluster'][id][3]/height
            break
    
    return_dict = {}
    return_dict['entity_lst'] = entity_lst
    return_dict['font_size'] = font_size
    return return_dict

