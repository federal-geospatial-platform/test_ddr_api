# -*- coding: utf-8 -*-
"""
This module executes the functionality test of the API created by Postman.
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
    """
    Class containing the result statistics of one collections.
    """

    def __init__(self, req_total, req_failed, assert_total, assert_failed, collection):

        self.req_total = req_total
        self.req_failed = req_failed
        self.assert_total = assert_total
        self.assert_failed = assert_failed
        self.collection = collection

        # Initialize the logger

        return

class TestApi:
    """
    Main class responsible to execute the API testing.
    """

    def __init__(self):

        self.test_success = True  # Initialize the test
        self.results = []  # Initialize the array of results
        self.html_files = []  # Initialise the list of attached/html files
        self.json_files = []  # Initialise the list of stats/json files

        return

    def __copy_json_documents(self):
        """
        Delete the content of the ./files diretory (content of the previous runs)

        :return: None
        """

        files = glob.glob('../file/*')
        for file in files:
            os.remove(file)

    def __read_yaml_file(self):
        """
        Read the YAML config file and store it in an instance variable

        :return:None
        """

        with open('config.yaml', 'r', encoding='utf-8') as file:
            self.config_yaml = yaml.safe_load(file)

        return

    def __execute_api_call(self, collection_name, mode):
        """
        This method executes the call the one request API call

        :param collection_name: Name of the collection
        :param mode: Internal or External call
        :return: None
        """

        # Extract the collection to process
        collection = self.config_yaml["collections"][collection_name]

        #Define file names
        json_file = f"{collection_name}_file.json"
        html_file = f"{collection_name}_file.html"

        # Extract the request
        request = collection["request"]

        # Extract the name
        var_url = collection["var_url"]
        url_internal = collection["url_internal"]

        export_files = f"--reporter-json-export ../files/{json_file} --reporter-html-export ../files/{html_file} "
        var_collection = f"--env-var {var_url}={url_internal} "
        command = request + " " + export_files + var_collection
        logging.info(command)
        ret = os.system(command)

        # Store the name of the html and json files
        self.html_files.append(f"../files/{html_file}")  # Add the name of the attached file
        self.json_files.append(f"../files/{json_file}")  # Add the name of the attached file

    def __build_email_body_text(self):
        """
        Build the email body text

        :return: None
        """

        HS = "&nbsp;&nbsp;"  # Hard space

        detailed_stats= "<p style=""font-family:'Courier New'"">"  # Contained the detailed statistics

        # Loop over each the result of each collection
        for result in self.results:
            if result.req_failed == 0 and result.assert_failed == 0:
                status_fr = "Succès"
                status_en = "Success"
            else:
                status_fr = "Échec"
                status_en = "Failure"
            self.tilte = f"{status_fr} - Résultat des tests de l'API / {status_en} - Result from API test <br>"
            detailed_stats += f"{HS}- {result.collection}: {status_fr} <br>"
            detailed_stats += f"{HS}{HS}- Requête: succès: {result.req_total - result.req_failed} <br>"
            detailed_stats += f"{HS}{HS}- Requête: échec: {result.req_failed} <br>"
            detailed_stats += f"{HS}{HS}- Assertion: succès: {result.assert_total - result.assert_failed} <br>"
            detailed_stats += f"{HS}{HS}- Assertion: échec: {result.assert_failed} <br><br>"

        # Is the overall API test was a succes
        if self.test_success:
            status_fr = "Succès"
            status_en = "Success"
            color = "green"  # Color of the Welcome message in the email body
        else:
            status_fr = "Échec"
            status_en = "Failure"
            color = "red"  # Color of the Welcome message in the email body

        # Build the email body
        self.body = ""
        self.body += "<b>DDR API Test</b> <br><br>"
        self.body += "(English message follows) <br><br>"
        self.body += "Bonjour,  <br>"
        self.body += f'<p style="color: {color}"><b><font size="+2">'  # Set the color of the title according to Success or Failure
        self.body += f"{status_fr} des tests de fonctionnalités de l'API / {status_en} of the API fonctionality TEST <br>"
        self.body += '<p style="color: black"></b>'  # Reset color to black
        self.body += "Voici les résultats détaillés du tests: <br>"
        self.body += detailed_stats

        # Build the email subject
        self.subject = f"{status_fr} des tests fonctionalité de l'API / {status_en} of the API functionality test"

    def __email_results(self):
        """
        Email the results using the information

        :return: None
        """

        # Build text body
        self.__build_email_body_text()

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

    def __extract_stats(self, collection):
        """
        Read the statistics in the JSON file

        :param collection: Name of the YAML collection to process
        :return: Class instance containing the result of the class
        """

        # Extract the name of the JSON file constaining the statistics
        json_report = self.json_files[-1]

        # Open the JSON report file
        handle = open(json_report)

        json_report = json.load(handle)  # Load the JSON file

        # Extract the content
        stats = json_report['run']['stats']
        req_total = stats['requests']['total']
        req_failed = stats['requests']['failed']
        assert_total = stats['assertions']['total']
        assert_failed = stats['assertions']['failed']

        logging.info(f"Total request: {req_total}; Request failed: {req_failed}; Total assertion: {assert_total}; Assertion failed: {assert_failed}")
        result = Result(req_total, req_failed, assert_total, assert_failed, collection)

        if req_failed != 0 or assert_failed != 0:
            self.test_success = False  # Set the test to failed

        return result

    def manage_api_testing(self):
        """
        This method manages the api testing by looping over each collection in the YAML, call the API

        :param mode:
        :return:
        """

        # Read the YAML configuration file
        self.__read_yaml_file()

        # Create the logger
        logging.basicConfig(filename=self.config_yaml["log"], filemode='a',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S", )

        # Copy the JSON collection documents
        self.__copy_json_documents()

        collections = self.config_yaml["collections"]
        for collection_name in collections:
            # Execute the API call using the newman application
            mode = None
            self.__execute_api_call(collection_name, mode)

            # Extract the statistics of the files
            result = self.__extract_stats(collection_name)
            self.results.append(result)

        # Send
        self.__email_results()


test_api = TestApi()
test_api.manage_api_testing()
