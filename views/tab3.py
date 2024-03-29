from flask import Blueprint, request, render_template, Response
import os
import csv
import subprocess

# Create a Blueprint object for Tab 3
tab3_bp = Blueprint('tab3', __name__, url_prefix='/tab3')

def create_csv_template(data, output_file_path, template_file_path):
    additional_string = "Unknown,Unknown,Department#Department#TRANSMISSION|Device-Type#Device-Type#TRS#Huawei|Device-Location#Device-Location|Device-Group#Device-Group#TRS#TRS_HUAWEI_MODEL|IPSEC#Is IPSEC Device|Device Type#All Device Types|Location#All Locations,,,,,,,,,,,,,,,,,,,,,,,,,,ENABLE_USING_COA,,,,,,,,CisC0IS3,OFF,Huawei,1700,FALSE,2083,,,ise-pan-mnt-ts01.starhubsg.sh.inc,,"
    additional_values = additional_string.split(',')

    # Read headers from the template CSV file
    with open(template_file_path, 'r') as template_file:
        csv_reader = csv.reader(template_file)
        headers = next(csv_reader)

    # Append data to the template file
    with open(output_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)  # Write headers to the CSV file
        for item in data:
            # Convert the OrderedDict to a list
            item.insert(2, item[1])
            if "ATN950D" in item[0]:
                item[1] = "Huawei, ATN950D"
            elif "ATN910CG" in item[0]:
                item[1] = "Huawei, ATN910CG"

            item[2] = item[2] + "/32"
            item.extend(additional_values)
            csv_writer.writerow(item)

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = [line.strip().split(',') for line in file]
    return data
@tab3_bp.route('/', methods=['GET', 'POST'])
def tab3_home():
    download_successful = None
    error_message=None
    if request.method == 'POST':
        input_text = request.form["NE"]
        with open('C:/Users/sutha/OneDrive/Desktop/blueprint/downloads/input.txt', 'w') as file:
            file.write(input_text)
        
        #script_path = '/home/rancid/test/app_ise.sh'
        #subprocess.run(['bash', script_path])

        output_data_path = 'C:/Users/sutha/OneDrive/Desktop/blueprint/downloads/output.txt'
        data = read_data_from_file(output_data_path)
        output_file_path = 'C:/Users/sutha/OneDrive/Desktop/blueprint/downloads/ise_output_file.csv'
        template_file='C:/Users/sutha/OneDrive/Desktop/blueprint/downloads/template.csv'
        create_csv_template(data, output_file_path, template_file)

        with open(output_file_path, 'rb') as file:
            csv_content = file.read()
        download_successful = 'File downloaded successfully'
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=ise_output_file.csv'},            
        )
        
    return render_template('tab3.html', download_successful=download_successful,error_message=error_message)
