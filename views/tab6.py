from flask import Blueprint, request, render_template, Response
import os
from werkzeug.security import generate_password_hash, check_password_hash
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

# Create a Blueprint object for Tab 6
tab6_bp = Blueprint('tab6', __name__, url_prefix='/tab6')

def run_selenium_script(userid,password,file):

    options=Options()
    options.add_experimental_option("detach",True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                            options=options)
    # Tell Selenium to wait for a maximum of 10 seconds for elements to appear
    wait = WebDriverWait(driver, 10)

    # Open the Google homepage
    driver.get("https://10.6.2.11/admin/login.jsp#administration/administration_networkresources/administration_networkresources_devices/networkdevices")
    driver.maximize_window()

    user_name = userid
    pass_word = password

    show_advanced = wait.until(EC.presence_of_element_located((By.ID, "details-button")))
    show_advanced.click()

    proceed_link = wait.until(EC.presence_of_element_located((By.ID, "proceed-link")))
    proceed_link.click()

    accept_button= wait.until(EC.presence_of_element_located((By.CLASS_NAME, "preLoginAcceptButton")))
    accept_button.click()

    username= wait.until(EC.presence_of_element_located((By.ID, "dijit_form_TextBox_0")))
    username.send_keys(user_name)

    password= wait.until(EC.presence_of_element_located((By.ID, "dijit_form_TextBox_1")))
    password.send_keys(pass_word)

    submit_button= wait.until(EC.presence_of_element_located((By.ID, "loginPage_loginSubmit")))
    submit_button.click()

    filter_button = wait.until(EC.presence_of_element_located((By.ID, "devicesTable_xwtTableContextualToolbar_FilterToggleButton")))
    filter_button.click()
    error_message=None

    with open(file, "r") as file:
        lines = file.readlines()
    deleted_ne = []
    ne_not_deleted=[]

    # Iterate through each line
    for line in lines:
        # Remove newline characters and leading/trailing whitespaces
        ne = line.strip()
        print(ne)
        NE_NAME = wait.until(EC.presence_of_element_located((By.ID, "xwt_widget_table__ByExampleWidget_0")))
        NE_NAME.clear()
        NE_NAME.send_keys(ne)
        time.sleep(5)
        try:
            # Proceed with the rest of the script
            check_box = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "selection-input")))
            if not check_box.is_selected():
                check_box.click()
            time.sleep(3)
            delete_button = wait.until(EC.presence_of_element_located((By.ID, "deleteBtnMenu_label")))
            delete_button.click()

            delete_selected = wait.until(EC.presence_of_element_located((By.ID, "deleteBtnMenuItem_text")))
            delete_selected.click()
            time.sleep(3)
            warning_pop_up = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='xwtAlert-warning']")))
            element_text = warning_pop_up.text

            target_text = "Are you sure you want to delete 1 device?"
            if target_text in element_text:
                print(f"Text '{target_text}' found on the page for NE:", ne)
                confirm_delete = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'xwt-TextButtonText') and text()='Delete']")))
                confirm_delete.click()
                deleted_ne.append(ne)

            else:
                #error_message="The text is not found on the page for {}".format(ne)
                ne_not_deleted.append(ne)
                #return error_message         
            # Add a wait statement
            time.sleep(3)
            
            # Perform actions for the current NE
            filter_button = wait.until(EC.presence_of_element_located((By.ID, "devicesTable_xwtTableContextualToolbar_FilterToggleButton")))
            filter_button.click()
            
            filter_button = wait.until(EC.presence_of_element_located((By.ID, "devicesTable_xwtTableContextualToolbar_FilterToggleButton")))
            filter_button.click()
        except Exception as e:
            # Check if the result is "No data available"
            no_data_message = wait.until(EC.presence_of_element_located((By.XPATH, "//div[text()='No data available']")))
            print("No data available message found for NE:", ne)
            ne_not_deleted.append(ne)
            continue
    success_message= "These are the NEs that are successfully deleted from ISE: {}".format(deleted_ne)
    error_message= "These are the NEs that were not deleted from ISE: {}".format(ne_not_deleted)
    
    return success_message,error_message

@tab6_bp.route('/', methods=['GET', 'POST'])
def tab6_home():
    execution_successful = None
    error_message=None
    if request.method == 'POST':
        input_text = request.form["NE"]
        filepath='C:/Users/sutha/OneDrive/Desktop/blueprint/deletion/input.txt'
        with open(filepath, 'w') as file:
            file.write(input_text)
        username=request.form["username"]
        password=request.form["password"]

        hashed_password = generate_password_hash(password)
        
        result_tuple = run_selenium_script(username, hashed_password, filepath)
        
        # Extract the success message and the error message from the tuple
        execution_successful, error_message = result_tuple


        
    return render_template('tab6.html', execution_successful=execution_successful,error_message=error_message)
