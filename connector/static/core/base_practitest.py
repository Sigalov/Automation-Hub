import datetime
import time
from enum import Enum
import json
from connector.static.core import static_methods
from connector.static.core.aws_sqs_pusher import SQSPusher


class BasePractiTest:
    WAIT_EXPONENTIAL_MULTIPLIER = 10000
    WAIT_EXPONENTIAL_MAX = 60000
    """
    Initializes the BasePractiTest class with various configurations and settings.

    :param pt_username: PractiTest username.
    :param pt_token: PractiTest API token.
    :param access_key: AWS access key for the user.
    :param secret_key: AWS secret key for the user.
    :param project_name: Name of the project in PractiTest.
    :param practitest_project_id: ID of the project in PractiTest.
    :param practitest_trigger_filter_id_list: List of filter IDs in PractiTest to trigger tests.
    :param practitest_execute_automated: Flag to determine if automated tests should be executed.
    :param practitest_automation_run_only: Filter tests to be executed by their statuses.
    :param processed_field_id: Field ID for the processed field in PractiTest.
    :param processed_field_value: Value for the processed field in PractiTest.
    :param practitest_automation_trigger: Trigger for automation in PractiTest.
    :param practitest_automation_trigger_value: Value for the automation trigger in PractiTest.
    :param practitest_aws_instance_type: Type of AWS instance to be used.
    :param practitest_debug: Debug flag, when True, the spot will no be terminated.
    :param execution_type: Type of execution to be performed.
    :param sync_exec: Flag to determine if execution should be synchronous.
    :param block: Block parameter (purpose to be defined based on code context).
    :param block_id: ID for the block.
    """

    def __init__(self, pt_username,
                 pt_token,
                 access_key,
                 secret_key,
                 project_name,
                 practitest_project_id,
                 practitest_trigger_filter_id_list=None,
                 practitest_execute_automated=None,
                 practitest_automation_run_only=None,
                 processed_field_id=None,
                 processed_field_value=None,
                 practitest_automation_trigger=None,
                 practitest_automation_trigger_value=None,
                 practitest_aws_instance_type=None,
                 practitest_debug=None,
                 execution_type=None,
                 sync_exec=None,
                 block=None,
                 block_id=None,
                 ):
        self.block = block
        self.block_id = block_id
        # PracitTest fields ID
        self.PRACTITEST_USER_NAME = pt_username
        self.PRACTITEST_API_TOKEN = pt_token
        self.AWS_ACCESS_KEY = access_key
        self.AWS_SECRET_KEY = secret_key
        self.PROJECT_NAME = project_name
        self.PRACTITEST_PROJECT_ID = practitest_project_id
        self.PRACTITEST_TRIGGER_FILTER_ID_LIST = practitest_trigger_filter_id_list
        self.PRACTITEST_EXECUTE_AUTOMATED = practitest_execute_automated
        self.PRACTITEST_AUTOMATION_RUN_ONLY = practitest_automation_run_only
        self.PROCESSED_FIELD_ID = processed_field_id
        self.PROCESSED_FIELD_VALUE = processed_field_value
        self.PRACTITEST_AWS_INSTANCE_TYPE = practitest_aws_instance_type
        self.PRACTITEST_DEBUG = practitest_debug
        self.EXECUTION_TYPE = execution_type
        self.SYNCHRONOUS_EXECUTION = sync_exec

        # Trigger fields
        self.PRACTITEST_AUTOMATION_TRIGGER = practitest_automation_trigger
        self.PRACTITEST_AUTOMATION_TRIGGER_VALUE = practitest_automation_trigger_value

        # PractiTest API URLs
        self.BASE_URL = "https://api.practitest.com/api/v2/projects/" + self.PRACTITEST_PROJECT_ID
        self.RUNS_URI = f'{self.BASE_URL}/runs.json?developer_email={self.PRACTITEST_USER_NAME}&api_token={self.PRACTITEST_API_TOKEN}'
        self.INSTANCE_URI = f'{self.BASE_URL}/instances.json?developer_email={self.PRACTITEST_USER_NAME}&api_token={self.PRACTITEST_API_TOKEN}'
        self.SETS_URI = f'{self.BASE_URL}/sets.json?developer_email={self.PRACTITEST_USER_NAME}&api_token={self.PRACTITEST_API_TOKEN}'
        self.SPECIFIC_SET_URI = f'{self.BASE_URL}/sets/YOUR_SET_ID.json?developer_email={self.PRACTITEST_USER_NAME}&api_token={self.PRACTITEST_API_TOKEN}'
        self.CLONE_TEST_SET = f'{self.BASE_URL}/sets/YOUR_SET_ID/clone.json?developer_email={self.PRACTITEST_USER_NAME}&api_token={self.PRACTITEST_API_TOKEN}'
        self.HEADERS = {
            'Content-Type': 'application/json',
            'Connection': 'close'
        }

    class TestStatusEnum(Enum):
        def __str__(self):
            return str(self.value)

        PASSED = 'PASSED'
        FAILED = 'FAILED'
        BLOCKED = 'BLOCKED'
        NO_RUN = 'NO RUN'
        N_A = 'N/A'


    def log(self, message):
        """
        Logs the provided message, storing it in the DB
        :param message: The message to be logged.
        """
        from connector.models import Block, LogEntry  # Import the Block and LogEntry models
        import datetime

        timestamp = datetime.datetime.now()
        log_with_timestamp = f"[{timestamp}] {message}"

        if self.block_id:
            block = Block.objects.get(pk=self.block_id)  # Fetch the block using block_id
            LogEntry.objects.create(block=block, content=log_with_timestamp, timestamp=timestamp)


    def get_dict_of_tests_objects(self, filter_test_sets_list):
        """
        Fetches a list of tests based on their status from the test set labeled as "Automation Run Only"
        and returns this list along with a list of Practitest test objects.

        Parameters:
        - filter_test_sets (list): A list of test sets to filter from.

        Returns:
        - list: A list of dictionaries where each dictionary represents a test containing:
            - project_name (str): Name of the project.
            - test_id (str): Display ID of the test.
            - test_instance (str): Unique ID representing the test instance.
            - test_name (str): Name of the test.
            - test_set_id (str): Display ID of the test set.
            - test_set_name (str): Name of the test set.
            - project_pt_id (str): Project ID from Practitest.
            - execution_session_id (str): Timestamp indicating the current execution session.
            - automation_run_only (str): Indicates if the test is for automation run only.
            - aws_instance_type (str): Specifies the AWS instance type.
            - debug (bool): Indicates if the test is in debug mode.
            - execution_type (str): Type of execution for the test.
            - sync_exec (bool): Indicates if the execution is synchronous.

        - list: A list of Practitest test objects.

        Raises:
        - Exception: If there's an error parsing the test set or test attributes.

        Notes:
        - If no test set is found under the specified filter, a warning will be logged.
        """
        initial_tests_list = [] #Contains all the tests to be executed (pushed to queue)
        if not filter_test_sets_list:
            self.log(f'Warning: No test set found under {self.PRACTITEST_TRIGGER_FILTER_ID_LIST} filter, but should be found')
            return

        filter_test_sets_dict = self.convert_test_set_obj_list_to_dict_set_id_as_key(filter_test_sets_list)
        tests = self.get_list_of_tests_by_status(filter_test_sets_dict)
        try:
            for test in tests:
                test_set = filter_test_sets_dict[str(test['attributes']['set-id'])]
                test_set_attributes = test_set['attributes']
                test_set_custom_fields = test_set_attributes['custom-fields']
                test_dict = {}
                test_attributes = test['attributes']
                test_custom_fields = test['attributes']['custom-fields']
                test_dict['project_name'] = self.PROJECT_NAME
                test_dict['test_id'] = str(test_attributes['test-display-id'])
                test_dict['test_instance'] = str(test['id']) #Unique test instance id, reporting back to PractiTest
                test_dict['test_name'] = str(test_attributes['name']).replace("'", "").replace('"', '').replace(',', '')\
                    .replace('(', '').replace(')', '').replace('<', '').replace('>', '').replace('!', '').replace('@', '')\
                    .replace('#', '').replace('*', '')
                test_dict['test_set_id'] = str(test_set_attributes['display-id'])
                test_dict['test_set_name'] = str(test_set_attributes['name'])
                test_dict['project_pt_id'] = str(test_attributes['project-id'])
                test_dict['execution_session_id'] = str(time.time()).replace(".","") #Timestamp for current execution, relevant for sync execution
                test_dict['automation_run_only'] = str(test_set_custom_fields[self.PRACTITEST_AUTOMATION_RUN_ONLY])
                test_dict['aws_instance_type'] = str(test_set_custom_fields[self.PRACTITEST_AWS_INSTANCE_TYPE])
                test_dict['debug'] = self.get_prioritized_value(self.PRACTITEST_DEBUG, test_set, test, is_boolean=True)
                test_dict['execution_type'] = str(self.EXECUTION_TYPE)
                test_dict['sync_exec'] = static_methods.try_to_get_from_dict(test_set_custom_fields, self.SYNCHRONOUS_EXECUTION, is_boolean=True)
                initial_tests_list.append(test_dict)
        except:
            self.log(f'Error: failed to parse test set/ test attributes')
        return initial_tests_list, tests


    def get_prioritized_value(self, dict_value, test_set, test, is_boolean=False):
        """
        Retrieve a prioritized value from either 'test', 'testset', or 'default' keys.

        This function tries to extract a value based on conditions specified in the input dict_value.
        It first checks the 'test' key, then 'testset', and finally the 'default' key. If none
        of these keys provide a value, an exception is raised.

        Parameters:
        - dict_value (dict): Dictionary containing keys ('test', 'testset', 'default') to specify the desired value.
        - test_set (dict): Dictionary containing the attributes of the test set.
        - test (dict): Dictionary containing the attributes of the test.
        - is_boolean: If true, it will convert 'yes'/'no' to 'true'/'false' string

        Returns:
        - value: The extracted value based on the conditions in dict_value.

        Raises:
        - ValueError: If the desired value cannot be retrieved.
        """

        test_set_attributes = test_set['attributes']
        test_set_custom_fields = test_set_attributes['custom-fields']
        test_attributes = test['attributes']
        test_custom_fields = test_attributes['custom-fields']


        # Helper function to extract value based on field name and source data
        def extract_value(field, attributes, custom_fields):
            if '---f-' in field:
                val = custom_fields[field]
            else:
                val = attributes[field]

            # Handle boolean conversion
            if is_boolean:
                if val == 'yes':
                    return 'true'
                elif val == 'no':
                    return 'false'
            return val

        try:
            # Check for 'test' key
            if 'test' in dict_value:
                return str(extract_value(dict_value['test'], test_attributes, test_custom_fields))
        except:
            pass
        try:
            # Check for 'testset' key
            if 'testset' in dict_value:
                return str(extract_value(dict_value['testset'], test_set_attributes, test_set_custom_fields))
        except:
            pass

        # Check for 'default' key
        if 'default' in dict_value:
            return str(dict_value['default'])

        # If none of the above conditions are met, raise an exception
        raise ValueError("Could not retrieve the desired field value.")


    def get_test_set_property(self, test_set_obj, test_set_property, is_custom_fields):
        """
        Retrieves a specified property from a test set object.

        :param test_set_obj: The test set object from which the property is to be extracted.
        :param test_set_property: The name of the property to retrieve.
        :param is_custom_fields: Boolean indicating whether the property is within the custom fields.
        :return: The value of the specified property. If the property is not found, logs an error message.

        Raises:
            Exception: If there's an issue retrieving the property, an error message is logged.
        """
        try:
            if is_custom_fields:
                val = test_set_obj['attributes']['custom-fields'][test_set_property]
            else:
                val = test_set_obj['attributes'][test_set_property]
            if not val:
                self.log(f'Failed to get test set property: "{is_custom_fields}", is custom field: "{str(is_custom_fields)}"')
        except:
            self.log('Failed to get test set property')


    def get_list_of_tests_by_status(self, test_set_obj_dict):
        """
        Fetches a list of tests based on their status and the Automation Run Only property of the associated test set.

        :param test_set_obj_dict: Dictionary of test set objects with set IDs as keys.
        :return: A list of test instances filtered by the Automation Run Only property of their associated test set.

        Note:
            The method utilizes pagination to fetch tests in batches. Each batch (or page) consists of up to 100 test instances.
            The function will keep fetching additional pages until a page with fewer than 100 test instances is encountered.
        """

        test_set_ids_list = list(test_set_obj_dict.keys())
        test_set_ids_list_str = ','.join(test_set_ids_list)
        tests_to_execute = []
        page = 1
        while True:
            url = self.INSTANCE_URI + "&set-ids=" + test_set_ids_list_str + "&page[number]=" + str(page)
            # For next iteration
            page = page + 1
            response = static_methods.wait_for_request_200('get', url, self.HEADERS, msg_on_retry=f'Bad response for get_list_of_tests_by_status; Going to retry')
            dct_sets = json.loads(response.text)
            if len(dct_sets["data"]) > 0:
                for test_instance in dct_sets["data"]:
                    test_instance_atrr = test_instance['attributes']
                    # If status is 'ALL', will add the test with any status
                    test_set_automation_run_only = test_set_obj_dict[str(test_instance['attributes']['set-id'])]['attributes']['custom-fields'][self.PRACTITEST_AUTOMATION_RUN_ONLY].lower()
                    if test_set_automation_run_only == 'all':
                        tests_to_execute.append(test_instance)
                    # Get only if the test matches to given status
                    elif test_instance_atrr['run-status'].lower() == test_set_automation_run_only:
                        tests_to_execute.append(test_instance)
            if len(dct_sets["data"]) < 100:
                break #Every page is 100 items, no need to get next page
        return tests_to_execute

    def convert_test_set_obj_list_to_dict_set_id_as_key(self, test_sets_list):
        """
        Converts a list of test set objects to a dictionary with set IDs as keys.
        :param test_sets_list: List of test sets objects.
        :return: A dictionary with test set IDs as keys and test set objects as values.
        """
        test_set_obj_dict = {}
        for test_set in test_sets_list:
            test_set_obj_dict[test_set['id']] = test_set
        return test_set_obj_dict

    def get_all_testsets_under_filter_list(self, filter_id:str):
        """
        Retrieves all test sets that fall under a given filter.
        :param filter_id: Filter ID
        :return: A list of test sets under the specified filters.
        """
        filter_id_list = filter_id.split(',')
        return self.get_all_testsets_under_filter_id_list(filter_id_list)


    def get_all_testsets_under_filter_id_list(self, filter_id_list):
        """
        Retrieves all test sets that fall under a given list of filters.
        :param filter_id_list: List of filter IDs.
        :return: A list of test sets under the specified filters.
        """
        testsets_list_of_dict = []
        for filter_id in filter_id_list:
            testsets_list_of_dict = testsets_list_of_dict + self.get_all_testsets_under_specific_filter_id(filter_id)
        return testsets_list_of_dict

    def get_all_testsets_under_specific_filter_id(self, filter_id):
        """
        Returns a dictionary containing all test sets associated with a specific filter ID.

        :param filter_id: ID of the filter, can be an integer or a string.
        :return: Dictionary containing test set data.
        """

        url = self.SETS_URI + "&filter-id=" + str(filter_id)
        response = static_methods.wait_for_request_200('get', url, self.HEADERS,
                                             f'Bad response for get_all_testsets_under_specific_filter_id; Going to retry')
        return static_methods.get_dict_data_if_not_empty(json.loads(response.text))

    def get_count_of_test_sets_under_filter(self, filter_id):#TODO add case: return only filters where there something to execute
        """
        Calculates the count of test sets under a given filter or list of filters.

        :param filter_id: Comma-separated string of filter IDs.
        :return: Total count of test sets under the provided filter(s).
        """

        filter_id_list = filter_id.split(',')
        count = 0
        for filter_id in filter_id_list:
            count = count + static_methods.safe_len(self.get_all_testsets_under_specific_filter_id(filter_id))
        return count

    def is_to_trigger(self):
        """
        Determines if there are any test sets under the specified filter ID.

        :return: True if there are test sets to be executed, otherwise False.
        """
        test_set_count = self.get_count_of_test_sets_under_filter(self.PRACTITEST_TRIGGER_FILTER_ID_LIST)
        if test_set_count > 0:
            self.log(f"{test_set_count} Testset/s found to execute")
            return True
        else:
            return False

    def push_to_sqs(self, tests_to_execute, debug=True):
        """
        Pushes test execution data to an SQS queue or, if in debug mode, writes the data to a JSON file.

        :param tests_to_execute: Dictionary containing details of tests to be executed.
        :param debug: Boolean indicating if the method is in debug mode. If True, data is written to a JSON file instead of SQS. Default is True.
        """
        if debug:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            filename = f'{timestamp}_to_execute.json'
            static_methods.write_dict_to_json_file(tests_to_execute, filename)
            self.log(f'JSON file: "{filename}" created')
            return
        self.log('Going to push to SQS')
        sqs_pusher = SQSPusher(access_key=self.AWS_ACCESS_KEY, secret_key=self.AWS_SECRET_KEY)
        sqs_pusher.push_to_queue()
        return