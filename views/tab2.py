from flask import Blueprint, render_template, request, redirect, current_app, flash
import os
from werkzeug.utils import secure_filename
import csv
import shutil

# Create a Blueprint object for Tab 2
tab2_bp = Blueprint('tab2', __name__, url_prefix='/tab2')

ALLOWED_EXTENSIONS = {'csv'}

# Function to check if a filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_and_append(source_csv_path, destination_txt_path):
    errors = []
    try:
        with open(source_csv_path, 'r', encoding='ISO-8859-1', newline='') as infile:
            csv_reader = csv.reader(infile)

            # Read the content of the first row (header)
            first_row = next(csv_reader, None)
            print("First row content:", first_row)

            # Check if the first cell contains the expected string "NE Report"
            if first_row is None or len(first_row) == 0 or not any("NE Report" in cell for cell in first_row):
                errors.append("The uploaded CSV file is not the correct file that contains the NE inventory")
                return errors

            # Skip the first three rows
            for _ in range(3):
                next(csv_reader)

            modified_rows = []
            for row in csv_reader:
                column2_value = row[1]
                column1_value = row[0]

                exclude_values = ['(5G)', 'SYNC', '5GTester', 'SNG/SHB/HKMEGAI32F-CX08-01']
                if column2_value in ['ATN950D', 'ATN910C-G', 'ATN950C', 'ATN910C-A', 'CX600-X1', 'CX600-X16', 'CX600-X1-M4', 'CX600-X8', 'CX600-X3'] and not any(exclude_value in column1_value for exclude_value in exclude_values):
                    concatenated_value = f"{column1_value}.pctn,{row[2]},vrp,pctn"
                    modified_rows.append(concatenated_value)

            modified_rows.sort()

            with open(destination_txt_path, 'w') as textfile:
                for sorted_row in modified_rows:
                    textfile.write(f"{sorted_row}\n")

            print("Filtered and sorted columns saved to", destination_txt_path)
    except FileNotFoundError:
        errors.append(f"Error: File '{source_csv_path}' not found.")
    except Exception as e:
        errors.append(f"Error: An unexpected error occurred: {e}")

    return errors

def append_lists(source_file_path, destination_file_path):
    errors = []
    with open(source_file_path, 'r') as source_file:
        source_list = source_file.read().splitlines()

    with open(destination_file_path, 'r') as destination_file:
        destination_lines = destination_file.read().splitlines()

    try:
        index = destination_lines.index("##### PCTN Devices")
    except ValueError:
        errors.append("Error: '##### PCTN Devices' not found in the destination file.")
        return errors

    destination_lines = destination_lines[:index + 1] + [""]+ source_list

    with open(destination_file_path, 'w') as destination_file:
        destination_file.write('\n'.join(destination_lines))

    return errors

def compare_inventory(file1_path, file2_path, difference_path):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2, open(difference_path, 'w') as f:
        file1_inventory = set(line.strip() for line in file1)
        file2_inventory = set(line.strip() for line in file2)

        # Items in file1 but not in file2
        removed_items = file1_inventory - file2_inventory

        # Items in file2 but not in file1
        added_items = file2_inventory - file1_inventory

        if removed_items:
            print("Items removed from file 2 compared to file 1:")
            f.write("NEs that have been removed from NCE:\n")
            for item in removed_items:
                print(item)
                f.write(item + '\n')

        if added_items:
            print("Items added to file 2 compared to file 1:")
            f.write("\n")
            f.write("\n")
            f.write("NEs that have been added to NCE:\n")
            for item in added_items:
                print(item)
                f.write(item + '\n')

        if not removed_items and not added_items:
            print("No differences found between the files.")
            f.write("No differences found between the files.")

# Define the route for Tab 2 home page
@tab2_bp.route('/', methods=['GET', 'POST'])
def tab2_home():
    upload_message = None
    error_message = None
    upload_folder = current_app.config['UPLOAD_FOLDER']  # Move this line here

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty part without filename
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Ensure the upload folder exists
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            cleaned_list = os.path.join(upload_folder, 'PCTN_NE.txt')
            router_db = "/home/rancid/router_db/router.db"
            router_old_db = "/home/rancid/router_db/router_old.db"
            difference_path = "/home/rancid/router_db/diff.txt"

            # Rename the existing router.db file to router_old.db if it exists
            if os.path.exists(router_db):
                shutil.copyfile(router_db, router_old_db)
            upload_errors = cleanup_and_append(file_path, cleaned_list)
            if upload_errors:
                error_message = '\n'.join(upload_errors)
            else:
                print("PCTN NEs have been extracted")
                upload_errors = append_lists(cleaned_list, router_db)
                if upload_errors:
                    error_message = '\n'.join(upload_errors)
                else:
                    print("routerdb file has been uploaded")
                    upload_message = 'File uploaded successfully'
                    compare_inventory(router_old_db,router_db,difference_path)
        else:
            error_message = 'Only CSV files are allowed.'

    # If it's a GET request or after processing a POST request, render the template
    return render_template('tab2.html', upload_message=upload_message, error_message=error_message)

