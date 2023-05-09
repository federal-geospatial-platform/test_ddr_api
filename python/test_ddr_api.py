# -*- coding: utf-8 -*-
"""
This module execute the functionality test on the DDR API.
"""

# Imports
# 3rd party imports
import os
import json
import yaml


# Application modules

class Result:

    def __init__(self, req_total, req_failed, assert_total, assert_failed):

        self.req_total = req_total
        self.req_failed = req_failed
        self.assert_total = assert_total
        self.assert_failed = assert_failed

        return

class Requests:

    def __init__(self):

        return

    def __read_yaml_file(self):

        with open('config.yaml', 'r', encoding='utf-8') as file:
            self.config_yaml = yaml.safe_load(file)

        print(self.config_yaml)
        collections = self.config_yaml["collections"]
        for collection in collections:
            print(self.config_yaml["collections"][collection])

        return

    def execute_api_call(self, collection=None, request=None):


        collection = "test"
        export_files =  f"--reporter-json-export {collection}.json --reporter-html-export {collection}.html"
        command = r"newman run C:\Users\dpilon\AppData\Local\Postman\app-10.13.0\DDR_Registry.json -g C:\Users\dpilon\AppData\Local\Postman\app-10.13.0\Globals.json -k -r html,json " + export_files
        print (command)
#        command = r"newman run C:\Users\dpilon\AppData\Local\Postman\app-10.13.0\DDR_Registry.json -g C:\Users\dpilon\AppData\Local\Postman\app-10.13.0\Globals.json -k -r html,json --reporter-json-export test.json --reporter-html-export test.html"
        ret = os.system(command)
        print ("retour =", ret)

    def email_result(self):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        mail_content = '''Hello,
        This is a simple mail. There is only text, no attachments are there The mail is sent using Python SMTP library.
        Thank You
        '''
        #The mail addresses and password
        sender_address = 'bergeronpilon@gmail.com'
        sender_pass = 'DanielGmail'
        receiver_address = 'bergeronpilon@gmail.com'
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'A test mail sent by Python. It has an attachment.'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')

    def manage_api_testing(self):
        # Read the YAML configuration file
        self.__read_yaml_file()

        collections = self.config_yaml["collections"]
        for collection in collections:
            request = self.config_yaml["collections"][collection]
            # self.execute_api_call(self, collection, request)

        self.email_result()


def extract_content(json_report):

    # Open the JSON report file
    handle = open(json_report)

    json_data = json.load(handle)

    stats = json_data['run']['stats']
    req_total = stats['requests']['total']
    req_failed = stats['requests']['failed']

    assert_total = stats['assertions']['total']
    assert_failed = stats['assertions']['failed']

    print (req_total, req_failed, assert_total, assert_failed)
    result = Result(req_total, req_failed, assert_total, assert_failed)
    return result



requests = Requests()

requests.manage_api_testing()

## Read the content of the YAML file
#requests.read_yaml_file()

# Clone the collections
#requests.clone_collections()

# Read the content of the YAML file
#requests.execute_api_call()

#extract_content()

#mail_results_()

print