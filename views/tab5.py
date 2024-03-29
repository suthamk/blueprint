# views/tab5.py
from flask import Blueprint, render_template, request, redirect, url_for
import subprocess

# Create a Blueprint object for Tab 5
tab5_bp = Blueprint('tab5', __name__, url_prefix='/tab5')

def extract_lines_with_CX01(input_text):
    lines_with_CX01 = []

    # Split the input text into lines
    lines = input_text.split('\n')
    
    for line in lines:
        if 'CX01' in line and "Detail" not in line and "ELL and mobile service migration to ATN/CX01M4 + node recovery" in line:
            lines_with_CX01.append(line.strip())

    modified_lines = [line.split('ELL')[0].split(':')[1].strip() for line in lines_with_CX01]

    return modified_lines

def search_router_db(ne_inputs, router_db_file):
    matching_lines = []
    with open(router_db_file, 'r') as file:
        for ne_input in ne_inputs:
            found = False
            for line in file:
                if ne_input in line:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        matching_lines.append((parts[0], parts[1]))
                    found = True
                    break  # Break the inner loop once a match is found
            if not found:
                matching_lines.append((ne_input, "Already removed from iNMS"))
            file.seek(0)  # Reset the file pointer to the beginning for the next ne_input

    return matching_lines

@tab5_bp.route('/', methods=['GET', 'POST'])
def tab5_home():
    result = None
    error_message=None
    input_txt_file = 'C:/Users/sutha/OneDrive/Desktop/blueprint/deletion/input.txt'
    if request.method == 'POST':
        if 'NE1' in request.form:
            input_text=request.form['NE1']
            clean_list=[]
            lines = input_text.split('\n')
            for line in lines:
                clean_list.append(line.strip())
            print(clean_list)
        if 'NE2' in request.form:
            input_text = request.form['NE2']
            clean_list = extract_lines_with_CX01(input_text)       
        valid_values = ["ATN950D", "CX01", "CX01M4", "ATN910CA","ATN910CG"]
        good_to_go=[]
        for item in clean_list:
            if any(value in item for value in valid_values):
                good_to_go.append(item)
            else:
                error_message = f"Error: '{item}' does not contain any valid value: {', '.join(valid_values)}"
        with open(input_txt_file, 'w') as file:
            for good_item in good_to_go:
                file.write(good_item + '\n')


        ###need to check NCE. Transfer the input file, run the NCE script, transfer back the ouput file
        #script_path = '/home/rancid/test/app_del.sh'
        #subprocess.run(['bash', script_path])


        with open('C:/Users/sutha/OneDrive/Desktop/blueprint/deletion/output.txt', 'r') as output_file:
            # Split the input_text into a list of lines and filter out empty lines
            ne_output = list(filter(None, output_file.read().splitlines()))

        # Search the router.db file line by line
        router_db_file = 'C:/Users/sutha/OneDrive/Desktop/blueprint/deletion/inms_pctn.txt'
        act_list=[]
        existing_ne=[]
        for i in ne_output:
            if "NOT FOUND IN NCE" in i:
                u=i.replace(',NOT FOUND IN NCE','')
                act_list.append(u)
            else:
                parts = i.split(',')
                existing_ne.append((parts[0], parts[1]))
        result = search_router_db(act_list, router_db_file)
        error_message= existing_ne
    
    return render_template('tab5.html', result=result,error_message=error_message)

