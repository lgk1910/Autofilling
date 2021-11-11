# Create and setup virtual environment
## Create virtual env
```
conda create -n autofilling python=3.7
```
## Install requirements
```
$git clone https://github.com/tesseract-ocr/tessdata

$curl https://raw.githubusercontent.com/oyyd/frozen_east_text_detection.pb/master/frozen_east_text_detection.pb --output frozen_east_text_detection.pb

$sudo apt-get update
$sudo add-apt-repository ppa:alex-p/tesseract-ocr
$sudo apt install tesseract-ocr
$sudo apt-get install poppler-utils

$pip install -r requirements.txt
```

# Run server
```
$python app.py
```

# Try sample requests
```
$python request.py
```

# Outputs
## Process 1 (detectfield)
The output of detectfield will be a file json object of the following format:
```
{
    "entity_lsts": [
        [
            {
                "name": <field_name>,
                "description": <field_name_with_vietnamese_accents>,
                "bb": [<left_x>, <top_y>, <width>, <height>] # scaled
            },
            ...
            {
                ...
            }
        ],
        ...
        [
            ...
        ]
    ],
    "font_size": <font_size> # scaled
}
```
* Note: `entity_lsts` is a list of lists, each of which represents a seperate page of the input pdf file. The order of them is also the order of the pages in the input file.

## Process 2 (`fillform`)
The output of `fillform` will be the input data with an additional `elapsed_time` attribute that represents the elapsed time of the process.

## Process 3 (`editform`)
The output of `editform` will be the same with that of detectfield with new fields added.

## `getjson`, `getresultform`, `getpdf`
For these three functions, the returns are json configuration file, latest filled form (after calling `fillform`) in pdf format, and the pre-filled pdf, respectively.











