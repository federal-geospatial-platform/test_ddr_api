# -*- coding: utf-8 -*-
"""
This module execute the functionality test on the DDR API.
"""

# Imports
# 3rd party imports
import os
import json
import yaml
import emails


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

        return

    def __read_yaml_file(self):

        with open('config.yaml', 'r', encoding='utf-8') as file:
            self.config_yaml = yaml.safe_load(file)

        print(self.config_yaml)
        collections = self.config_yaml["collections"]
        for collection in collections:
            print(self.config_yaml["collections"][collection])

        return

    def execute_api_call(self, collection_name, mode):

        # Extract the collection to process
        collection = self.config_yaml["collections"][collection_name]

        # Extract the request
        request = collection["request"]

        # Extract
        var_url = collection["var_url"]
        url_internal = collection["url_internal"]

        export_files = f"--reporter-json-export {collection_name}_file.json --reporter-html-export {collection_name}_file.html "
        var_collection = f"--env-var {var_url}={url_internal} "
        command = request + " " + export_files + var_collection
        print(command)
        ret = os.system(command)
        print ("retour =", ret)

    def email_result(self):

        # Prepare the email
        message = emails.html(html="voici le text", subject="Sujet", mail_from="ddr.fgpservices-servicespgf.rdd@aws.nrcan-rncan.cloud")

        # message.cc = config_env.EMAIL_ADMIN

        # Send the email
        r = message.send(
            to="bergeronpilon@gmail.com",
            smtp={
                "host":"email-smtp.ca-central-1.amazonaws.com",
                "port": 587,
                "timeout": 10,
                "user": "AKIARHK2ZDWAX5LTKCJH",
                "password": "BCpDDYnkVsrj8gvCTu7LliMq8+ie4C/JB6QZAEByLuVK",
                "tls": True
            }
        )

    def extract_stats(self, collection):

        json_report = collection + "_file.json"

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
        return result

    def manage_api_testing(self, mode):

        # Read the YAML configuration file
        self.__read_yaml_file()

        collections = self.config_yaml["collections"]
        self.results = []  # Initialize the array of results
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


