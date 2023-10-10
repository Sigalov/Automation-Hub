import logging
import time
from enum import Enum
import json
from connector.static.core import static_methods
from connector.static.core.aws_sqs_pusher import SQSPusher


class BasePractiTest:
    WAIT_EXPONENTIAL_MULTIPLIER = 10000
    WAIT_EXPONENTIAL_MAX = 60000

    def __init__(self, pt_username,
                 filter_id_list,
                 pt_token,
                 access_key,
                 secret_key,
                 project_name,
                 practitest_project_id,
                 practitest_trigger_filter_id=None,
                 practitest_execute_automated=None,
                 practitest_automation_run_only=None,
                 processed_field_id=None,
                 processed_field_value=None,
                 practitest_automation_trigger=None,
                 practitest_automation_trigger_value=None,
                 practitest_aws_instance_type=None,
                 practitest_debug=None,
                 execution_type=None,
                 sync_exec=None
                 ):
        # PracitTest fields ID
        self.PRACTITEST_USER_NAME = pt_username
        self.PRACTITEST_TRIGGER_FILTER_ID_LIST = filter_id_list
        self.PRACTITEST_API_TOKEN = pt_token
        self.AWS_ACCESS_KEY = access_key
        self.AWS_SECRET_KEY = secret_key
        self.PROJECT_NAME = project_name
        self.PRACTITEST_PROJECT_ID = practitest_project_id
        self.PRACTITEST_EXECUTE_AUTOMATED = practitest_execute_automated
        self.PRACTITEST_AUTOMATION_RUN_ONLY = practitest_automation_run_only
        self.PROCESSED_FIELD_ID = processed_field_id
        self.PROCESSED_FIELD_VALUE = processed_field_value
        self.PRACTITEST_TRIGGER_FILTER_ID = practitest_trigger_filter_id
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

    def create_tests_json(self, filter_test_sets):
        tests_dict = [] #Contains all the tests to be executed (pushed to queue)
        if not filter_test_sets:
            logging.info(f'Warning: No test set found under {self.PRACTITEST_TRIGGER_FILTER_ID} filter, but should be found')
            return
        for test_set in filter_test_sets:
            try:
                test_set_attributes = test_set['attributes']
                test_set_custom_fields = test_set['attributes']['custom-fields']
                tests = self.get_list_of_tests_by_status(test_set, 'all')
                for test in tests:
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
                    tests_dict.append(test_dict)
            except:
                logging.info(f'Error: failed to parse test set/ test attributes')
        return tests_dict

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

    def get_list_of_tests_by_status(self, test_set_id, status):
        """Return all test sets under specific filter id
        :param test_set_id: test set id as int or string
        :param status: TestStatusEnum: PASSED, FAILED, BLOCKED, NO_RUN, N_A, ALL
        :return: dictionary
        """
        tests_to_execute = []
        page = 1
        while True:
            url = self.INSTANCE_URI + "&set-ids=" + str(test_set_id['id']) + "&page[number]=" + str(page)
            # For next iteration
            page = page + 1
            response = static_methods.wait_for_request_200('get', url, self.HEADERS,
                                                 f'Bad response for get_list_of_tests_by_status; Going to retry')
            dct_sets = json.loads(response.text)
            if len(dct_sets["data"]) > 0:
                for test_instance in dct_sets["data"]:
                    test_instance_atrr = test_instance['attributes']
                    # If status is 'ALL', will add the test with any status
                    if status.lower() == 'all':
                        tests_to_execute.append(test_instance)
                    # Get only if the test matches to given status
                    elif test_instance_atrr['run-status'].lower() == status.lower():
                        tests_to_execute.append(test_instance)
            else:
                if page <= 2:
                    logging.info("No instances in set. " + response.text)
                break
                # if page > 2:
                #     logging.info("Finished getting tests from test set: '" + test_set_id['attributes']['name'] +
                #           "' ID: " + str(test_set_id['attributes']['display-id']))
                # else:
                #     logging.info("No instances in set. " + response.text)
                # break
        return tests_to_execute

    def get_all_testsets_under_specific_filter_id(self, filter_id):
        """Return all test sets under specific filter id
        :param filter_id: filter id as int ot string
        :return: dictionary
        """
        url = self.SETS_URI + "&filter-id=" + str(filter_id)
        response = static_methods.wait_for_request_200('get', url, self.HEADERS,
                                             f'Bad response for get_all_testsets_under_specific_filter_id; Going to retry')
        return static_methods.get_dict_data_if_not_empty(json.loads(response.text))

    def get_count_of_test_sets_under_filter(self, filter_id):
        return static_methods.safe_len(self.get_all_testsets_under_specific_filter_id(filter_id))

    def is_to_trigger(self):
        """Return True if there are test sets under specific filter (PRACTITEST_TRIGGER_FILTER_ID) from json
        :return: True or False
        """
        if self.get_count_of_test_sets_under_filter(self.PRACTITEST_TRIGGER_FILTER_ID) > 0:
            return True
        else:
            return False

    def push_to_sqs(self, tests_to_execute, debug=True):
        if debug:
            static_methods.write_dict_to_json_file(tests_to_execute, 'tests_to_execute.json')
            return
        sqs_pusher = SQSPusher(access_key=self.AWS_ACCESS_KEY, secret_key=self.AWS_SECRET_KEY)
        sqs_pusher.push_to_queue()
        return