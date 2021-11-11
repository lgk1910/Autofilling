import requests
import string
import json
import re
import os

BASE = "http://127.0.0.1:5000/"

# input_url = input("URL: ")
input_for_process_1 = {
    "form_code": "form4",
    "url": "https://www.ucrhealth.org/wp-content/uploads/2020/04/sample.pdf"
}

input_for_process_2 = {
    "form_code": "form3",
    "data": "[[{'name': 'so_no_1', 'data': '1234'}, {'name': 'hop_dong_lien_ket_nay_hop_dong_duoc_ky_ket_vao_ngay_1',  'data': '11/12/2021'}, {'name': 'cooperation_agreement_mgreemen_t_125_made_on_1',  'data': '11/12/2021'}, {'name': 'p_artya_1',  'data': 'trường Đại học Bách Khoa TP.HCM'}, {'name': 'dia_chi_address_1',  'data': '268 Lý Thường Kiệt'}, {'name': 'code_1',  'data': 'Mã Số CN 1'}, {'name': 'dien_thoai_te_1',  'data': '0707080805'}, {'name': 'fax_1',  'data': 'Số fax Bách Khoa'}, {'name': 'ong_ba_mr_ms_1',  'data': 'Nguyễn Văn A'}, {'name': 'chuc_vu_tit_e_1',  'data': 'Giám Đốc'}, {'name': 'partyb_1',  'data': 'Rever'}, {'name': 'dia_chi_address_2',  'data': 'TP.HCM'}, {'name': 'ma_so_thue_tax_code_1',  'data': 'Mã số thuế Rever'}, {'name': 'dien_thoai_te_2',  'data': '0987678987'}, {'name': 'account_name_1',  'data': 'Rever'}, {'name': 'number_1',  'data': '00001028380401819'}, {'name': 'ngan_hang_bank_1',  'data': 'Ngân Hàng Rever'}, {'name': 'chi_nha_nh_branch_1',  'data': 'Rever - TP.HCM'}, {'name': 'eng_ba_mr_ms_1',  'data': 'Nguyễn Thị B'}, {'name': 'chuc_vu_tit_e_2',  'data': 'Giám Đốc'}]]"
}

input_for_process_3 = {
    "form_code": "form3",
    "new_entities": [
            [
                {
                    "name": "new_entity_1",
                    "bb": [0.001, 0.02, 0.3, 0.004]
                }
            ]
        ]
}

form_code = "form3"

try:
    # Test process 1
    res = requests.post(BASE + 'detectfield', 
                        json=input_for_process_1)
    parsed_json_res = res.json()
    print(f"Output 1:\n {json.dumps(parsed_json_res, indent=4, sort_keys=True)}")

    # Test process 2
    res = requests.post(BASE + 'fillform', 
                        json=input_for_process_2)
    parsed_json_res = res.json()
    print(f"Output 2:\n {json.dumps(parsed_json_res, indent=4, sort_keys=True)}")

    # Test process 3
    res = requests.post(BASE + 'editform', 
                        json=input_for_process_3)
    parsed_json_res = res.json()
    print(f"Output 3:\n {json.dumps(parsed_json_res, indent=4, sort_keys=True)}")

    # Get result json
    res = requests.get(BASE + 'getjson/' + form_code)
    parsed_json_res = res.json()
    print(f"Output 4:\n {json.dumps(parsed_json_res, indent=4, sort_keys=True)}")

    # Get result form
    res = requests.get(BASE + 'getresultform/' + form_code)

    # Get pdf
    res = requests.get(BASE + 'pdf/' + form_code)

except:
    print("Failed to send request")