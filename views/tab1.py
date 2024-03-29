# views/tab1.py
from flask import Blueprint, request, render_template, Response
import os
import csv
from openpyxl import load_workbook
import subprocess

# Create a Blueprint object for Tab 1
tab1_bp = Blueprint('tab1', __name__, url_prefix='/tab1')

@tab1_bp.route('/', methods=['GET', 'POST'])
def tab1_home():
    form_submitted= False
    data=[]
    if request.method == 'POST':
        # Get user input from the form as a string
        input_text = request.form['NE']

        # Write the user input directly to the input.txt file
        input_txt_file = 'C:/Users/sutha/OneDrive/Desktop/blueprint/insertion/input.txt'
        with open(input_txt_file, 'w') as file:
            file.write(input_text)

        # Execute the script located in /home/rancid/test
        #script_path = '/home/rancid/test/sutha.sh'
        #subprocess.run(['bash', script_path])

        # Read the output CSV file
        output_csv_file = 'C:/Users/sutha/OneDrive/Desktop/blueprint/insertion/output.csv'
        with open(output_csv_file, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data = [row for row in csv_reader]

        # Set the form submitted flag to True
        form_submitted = True

    return render_template('tab1.html', form_submitted=form_submitted, data=data)
