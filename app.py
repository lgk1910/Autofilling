from flask import Flask, render_template, request, jsonify, send_file
import time
import glob
import re
import json
import urllib.request 
import os
import numpy as np
import model
from PIL import Image
import requests
import wget
import json 

app = Flask(__name__)

FONTPATH = "fonts/arial.ttf"
JSONPATH='static/jsons/'
PDFPATH= 'static/pdfs/'
RESULTPATH='static/results/'

if not os.path.exists('static'):
    os.makedirs('static')
    if not os.path.exists('static/jsons'):
        os.makedirs('static/jsons')
    if not os.path.exists('static/pdfs'):
        os.makedirs('static/pdfs')
    if not os.path.exists('static/results'):
        os.makedirs('static/results')

@app.route('/')
def home():
    return "Fields Autodetection and Autofilling"

@app.route('/detectfield',methods=['GET', 'POST'])
def detectfeild():
  if request.method=='POST':
    execution_time=time.time()
    data=request.get_json()
    form_code=data['form_code']
    url=data['url']
    print(url)
    # down file về để lưu vào ./static/pdfs/<form_code>.pdf

    if url.endswith('.pdf'):
      print("download {} pdf file ...".format(form_code))
      wget.download(url, os.path.join(PDFPATH, form_code + '.pdf'))
    else:
      print("download {} image and convert to pdf file ...".format(form_code))
      image = Image.open(requests.get(url, stream=True).raw)
      image.save(PDFPATH+form_code+'.pdf')

    # detect ra fields và lưu json vào ./static/json/<form_code> 
    print("detect feilds from {} ...".format(form_code)) 
    entity_lsts, font_size = model_.process_1(PDFPATH+form_code+'.pdf')
    json_dummy={"entity_lsts":entity_lsts,"font_size":font_size,"time":time.time() - execution_time}
    #res_json = jsonify(entity_lsts=entity_lsts, font_size = font_size, time=time.time() - execution_time)
    with open(JSONPATH+form_code+'.json', 'w') as f:
      json.dump(json_dummy, f)
    return jsonify(json_dummy)

  return {'message':'You need to use POST metod'}

@app.route('/fillform',methods=['GET', 'POST'])
def fillform():
  if request.method=='POST':
    start_time = time.time()
    data=request.get_json()
    form_code=data['form_code'] # lấy cái này để tra ra bouding box, fontsize
    input_data = data['data'] # thông tin các fields
    # điền form và lưu file đã điền  ./static/pdfs/<form_code>
    # load json configuration file
    filepath = os.path.join(JSONPATH, form_code + '.json')
    with open(filepath) as json_file:
        config = json.load(json_file)

    # get entity lists, font_size and input_data
    font_size = config['font_size']
    entity_lsts = config['entity_lsts']
    input_data = list(eval(input_data))

    # Read and merge data with configuration 
    entity_dict_list = []
    for page in input_data:
        entity_dict = {}
        for entity in page:
            entity_dict[entity['name']] = entity['data']
        entity_dict_list.append(entity_dict)

    for lst_id, entity_lst in enumerate(entity_lsts):
        entity_dict = entity_dict_list[lst_id]
        for entity in entity_lst:
            try:
                entity['data'] = entity_dict[entity['name']]
            except:
                pass

    # Run the autofilling engine
    pdf_path = os.path.join(PDFPATH, form_code + '.pdf')
    model_.process_2(pdf_path, entity_lsts, font_size, FONTPATH, form_code, RESULTPATH)
    data['elapsed_time'] = time.time()-start_time
    return data
  return {'message':'You need to use POST metod'}

@app.route('/editform',methods=['GET', 'POST'])
def editform():
  if request.method=='POST':
    data=request.get_json()
    form_code=data['form_code'] # code của form muốn thêm feild
    new_entities = data['new_entities'] # element muốn thêm (bao gồm bb và tên feild)
    # edit lại json và lưu vào   ./static/json/<form_code>
    
    # load json configuration file
    filepath = os.path.join(JSONPATH, form_code + '.json')
    with open(filepath) as json_file:
        config = json.load(json_file)

    # get entity lists, font_size and input_data
    font_size = config['font_size']
    entity_lsts = config['entity_lsts']

    # new_entities: [  [{},{'name':,'bb':}] , [] ]
    # entity_lsts:  [  [{},{'name':,'bb':}] , [] ]
    # extract new entities and append 
    for page_number, page in enumerate(new_entities):
      for entity in page:
        entity_lsts[page_number].append(entity)

    #save json file with edited entity_list
    json_dummy={"entity_lsts":entity_lsts,"font_size":font_size}
    with open(JSONPATH+form_code+'.json', 'w') as f:
      json.dump(json_dummy, f)
    return jsonify(json_dummy)

  return {'message':'You need to use POST metod'}

@app.route('/getjson/<form_code>')
def getjson(form_code):
  return send_file('static/jsons/'+form_code+'.json',as_attachment=False)

@app.route('/getresultform/<form_code>')
def getresultform(form_code):
  return send_file('static/results/'+form_code+'.pdf',as_attachment=False)

@app.route('/pdf/<form_code>')
def test(form_code):
  return send_file('static/pdfs/'+form_code+'.pdf',as_attachment=False,download_name=form_code)

if __name__ == '__main__':
    model_ = model.Model()
    app.run()