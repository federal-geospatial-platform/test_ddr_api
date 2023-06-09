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
import boto3
from botocore.exceptions import ClientError

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

        # Test if the program is run in a docker environment or not
        if os.environ.get('RUN_DOCKER') is not None:
            self.docker_run = True
        else:
            self.docker_run = False

        if self.docker_run:
            self.newman_path = "/etc/app/newman/"
            self.log_path = "/etc/app/log/"

        else:
            self.newman_path = "../newman/"
            self.log_path = "../log/"

        return

    def __get_aws_secret(self):

        region_name = "ca-central-1"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        # Extract the credentials for the AWS email
        try:
            secret_name = "test/api/db"
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response['SecretString']

        # store the secret as a JSON properties
        self.aws_secret_json = json.loads(secret)

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

    def __extract_db_credentials(self, collection_name):
        """
        This method reafd the DB credetials according to the name of the collection.

        If the username/password is null the value "dummy" is placed instead.

        :param collection_name: Name of the collection
        :return: String containing the username and password to be used.
        """

        # Read the username and password in the AWS secret
        credentials = self.aws_secret_json[collection_name]
        username = credentials["user"]
        password = credentials["pass"]

        if username is None:
            username = "dummy"

        if password is None:
            password = "dummy"

        return (username, password)

    def __execute_api_call(self, collection_name):
        """
        This method executes the call the one request API call

        :param collection_name: Name of the collection
        :param mode: Internal or External call
        :return: None
        """

        # Extract the collection to process
        collection = self.config_yaml["collections"][collection_name]

        # Define file names
        json_file = f"{collection_name}_file.json"
        html_file = f"{collection_name}_file.html"

        # Extract the request
        request = collection["request"]

        # Extract the name
        var_url = self.config_yaml["var_url"]  # Name of the environment variable containing the prefix of the request
        url_internal = collection["url_internal"]  # Flag indicating if it's an IP address or a regular address

        export_files = f"--reporter-summary-json-export ../files/{json_file} --reporter-html-export ../files/{html_file} "

        # Extract the database credentials
        (username,password) = self.__extract_db_credentials(collection_name)

        ddr_api_db = f' --env-var "username={username}" --env-var "password={password}"'

        if self.config_yaml["mode"] == "url_internal":  # IP address
            # Change the URL for URL of th ip address
            var_collection = f"--env-var {var_url}={url_internal} "
        else:
            var_collection = ""

        command = request + " " + export_files + var_collection + ddr_api_db

        # Adjust the the file paths
        command = command.replace("newman_path::", self.newman_path)
        ret = os.system(command)

        # Remove the username and password from the command before logging the command
        command = command.replace(username, "???")
        command = command.replace(password, "???")
        logging.info(command)
        print(command)

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
                color = "green"
            else:
                status_fr = "Échec"
                status_en = "Failure"
                color = "red"
            self.tilte = f"{status_fr} - Résultat des tests de l'API / {status_en} - Result from API test <br>"
            detailed_stats += f'<body style="color: {color}">'
            detailed_stats += f"{HS}- {result.collection}: {status_fr}:<br>"
            detailed_stats += '<body style="color: black">'  # Reset color to black
            detailed_stats += f"{HS}{HS}- Requête: succès: {result.req_total - result.req_failed} <br>"
            detailed_stats += f"{HS}{HS}- Requête: échec: {result.req_failed} <br>"
            detailed_stats += f"{HS}{HS}- Assertion: succès: {result.assert_total - result.assert_failed} <br>"
            detailed_stats += f"{HS}{HS}- Assertion: échec: {result.assert_failed} <br><br>"

        # Is the overall API test was a succes
        if self.test_success:
            status_fr = "Succès"
            status_en = "Success"
        else:
            status_fr = "Échec"
            status_en = "Failure"

        # Build the email body
        self.body = ""
        self.body += "<b>DDR API Test</b> <br><br>"
        self.body += "(English message follows) <br><br>"
        self.body += "Bonjour,<br><br>"
        self.body += "Voici les résultats détaillés des tests: <br>"
        self.body += detailed_stats

        # Build the email subject
        self.subject = f"{status_fr} des tests de fonctionalité de l'API / {status_en} of the API functionality test"

    def __email_results(self):
        """
        Email the results using the information

        :return: None
        """

        # Build text body
        self.__build_email_body_text()

        # Prepare the email
        message = emails.html(html=self.body, subject=self.subject, mail_from=self.aws_secret_json["email"]["from"])

        for html_file in self.html_files:
            message.attach(data=open(html_file, "rb"), filename=html_file)

        # message.cc = config_env.EMAIL_ADMIN

        # Send the email
        r = message.send(
            to=self.config_yaml["to"],
            smtp={
                "host": self.aws_secret_json["email"]["host"],
                "port": self.aws_secret_json["email"]["port"],
                "timeout": self.aws_secret_json["email"]["timeout"],
                "user": self.aws_secret_json["email"]["user"],
                "password": self.aws_secret_json["email"]["pass"],
                "tls": self.aws_secret_json["email"]["tls"]
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
        stats = json_report['Run']['Stats']
        req_total = stats['Requests']['total']
        req_failed = stats['Requests']['failed']
        assert_total = stats['Assertions']['total']
        assert_failed = stats['Assertions']['failed']

        print (f"Total request: {req_total}; Request failed: {req_failed}; Total assertion: {assert_total}; Assertion failed: {assert_failed}")
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

        # Read the AWS secret messages
        self.__get_aws_secret()

        # Read the YAML configuration file
        self.__read_yaml_file()

        # If the folder doesn't exist, create it
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        # Create the logger
        log_file = self.config_yaml["log"]

        # Adjust file path
        log_file = log_file.replace("log_path::", self.log_path)

        # Set the logging
        logging.basicConfig(filename=log_file, filemode='a',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S", )

        # Copy the JSON collection documents
        self.__copy_json_documents()

        collections = self.config_yaml["collections"]
        for collection_name in collections:
            # Execute the API call using the newman application
            self.__execute_api_call(collection_name)

            # Extract the statistics of the files
            result = self.__extract_stats(collection_name)
            self.results.append(result)

        # Send
        self.__email_results()

test_api = TestApi()
test_api.manage_api_testing()
