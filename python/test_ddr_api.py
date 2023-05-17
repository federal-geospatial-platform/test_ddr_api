# -*- coding: utf-8 -*-
"""
This module execute the functionnality test of the API created by Postman..
"""

# Imports
# 3rd party imports
import os
import glob
import json
import yaml
import emails
import logging

# Application modules

class Result:

    def __init__(self, req_total, req_failed, assert_total, assert_failed, collection):

        self.req_total = req_total
        self.req_failed = req_failed
        self.assert_total = assert_total
        self.assert_failed = assert_failed
        self.collection = collection

        return

class Requests:

    def __init__(self):

        self.test_success = True  # Initialize the test
        self.results = []  # Initialize the array of results
        self.html_files = []  # Initialise the list of attached/html files
        self.json_files = []  # Initialise the list of stats/json files

        return

    def __copy_json_documents(self):

        # Delete the content of the ./files diretory
        files = glob.glob('../file/*')
        for file in files:
            os.remove(file)

#        # Copy the JSON collection from the GitHub to the ./files directory
#        collections = self.config_yaml["collections"]
#        for collection in collections:
#            github = collections[collection]['github']
#            command = f"git clone {github} ../files"
#            ret = os.system(command)



    def __read_yaml_file(self):

        with open('config.yaml', 'r', encoding='utf-8') as file:
            self.config_yaml = yaml.safe_load(file)

        print(self.config_yaml)
        collections = self.config_yaml["collections"]
        for collection in collections:
            print(self.config_yaml["collections"][collection])

        return

    def execute_api_call(self, collection_name, mode):

        # Initialize the logger
        logging.basicConfig(filename=self.config_yaml["log"], filemode='a',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S",)

        # Extract the collection to process
        collection = self.config_yaml["collections"][collection_name]

        #Define files
        json_file = f"{collection_name}_file.json"
        html_file = f"{collection_name}_file.html"

        # Extract the request
        request = collection["request"]

        # Extract
        var_url = collection["var_url"]
        url_internal = collection["url_internal"]

        export_files = f"--reporter-json-export ../files/{json_file} --reporter-html-export ../files/{html_file} "
        var_collection = f"--env-var {var_url}={url_internal} "
        command = request + " " + export_files + var_collection
        logging.info(command)
        ret = os.system(command)
        print ("retour =", ret)

        self.html_files.append(f"../files/{html_file}")  # Add the name of the attached file
        self.json_files.append(f"../files/{json_file}")  # Add the name of the attached file

    def _build_email_body_text(self):



        HS = "&nbsp;&nbsp;"
        detailed_stats= ""
        for result in self.results:
            if result.req_failed == 0 and result.assert_failed == 0:
                status_fr = "Succès"
                status_en = "Success"
            else:
                status_fr = "Échec"
                status_en = "Failure"
            self.tilte = f"{status_fr} - Résultat des test de l'API / {status_en} - Result from API test <br>"
            detailed_stats += f"{HS}- {result.collection}: {status_fr} <br>"
            detailed_stats += f"{HS}{HS}- Requête: succès: {result.req_total - result.req_failed} <br>"
            detailed_stats += f"{HS}{HS}- Requête: échec: {result.req_failed} <br>"
            detailed_stats += f"{HS}{HS}- Assertion: succès: {result.assert_total - result.assert_failed} <br>"
            detailed_stats += f"{HS}{HS}- Assertion: échec: {result.assert_failed} <br><br>"

        if self.test_success:
            status_fr = "Succès"
            status_en = "Success"
        else:
            status_fr = "Échec"
            status_en = "Failure"
        self.body = ""
        self.body += "DDR API Test <br><br>"
        self.body += "(English message follows) <br><br>"
        self.body += "Bonjour,  <br><br>"
        self.body += f"{status_fr} des tests de fonctionnalités de l'API / {status_en} of the API fonctionality TEST <br><br>"
        self.body += "Voici les résultats détaillés du tests: <br><br>"
        self.body += detailed_stats

        self.subject = f"{status_fr} des test fonctionalité de l'API / {status_en} of the API functionality test"

    def email_result(self):

        # Build text body
        self._build_email_body_text()

        # Prepare the email
        message = emails.html(html=self.body, subject=self.subject, mail_from="ddr.fgpservices-servicespgf.rdd@aws.nrcan-rncan.cloud")

        for html_file in self.html_files:
            message.attach(data=open(html_file, "rb"), filename=html_file)

        # message.cc = config_env.EMAIL_ADMIN

        # Send the email
        r = message.send(
            to=self.config_yaml["email"]["to"],
            smtp={
                "host":self.config_yaml["email"]["host"],
                "port": self.config_yaml["email"]["port"],
                "timeout": self.config_yaml["email"]["timeout"],
                "user": self.config_yaml["email"]["user"],
                "password": self.config_yaml["email"]["password"],
                "tls": self.config_yaml["email"]["tls"]
            }
        )

    def extract_stats(self, collection):

        json_report = self.json_files[-1]

        # Open the JSON report file
        handle = open(json_report)

        json_report = json.load(handle)

        stats = json_report['run']['stats']
        req_total = stats['requests']['total']
        req_failed = stats['requests']['failed']

        assert_total = stats['assertions']['total']
        assert_failed = stats['assertions']['failed']

        print(req_total, req_failed, assert_total, assert_failed)
        result = Result(req_total, req_failed, assert_total, assert_failed, collection)

        if req_failed != 0 or assert_failed != 0:
            self.test_success = False  # The test failed
        return result

    def manage_api_testing(self, mode):

        # Read the YAML configuration file
        self.__read_yaml_file()

        # Copy the JSON collection documents
        self.__copy_json_documents()

        collections = self.config_yaml["collections"]
        for collection_name in collections:
            # Execute the API call using the newman application
            self.execute_api_call(collection_name, mode)

            # Extract the statistics of the files
            result = self.extract_stats(collection_name)
            self.results.append(result)

        # Send
        self.email_result()


requests = Requests()

mode = "internal"
requests.manage_api_testing(mode)


