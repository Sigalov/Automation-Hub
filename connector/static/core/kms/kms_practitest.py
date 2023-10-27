from time import sleep
from connector.static.core.base_practitest import BasePractiTest
from connector.static.core.static_methods import try_to_get_from_dict

class KmsPractiTest(BasePractiTest):
    def __init__(self, more_data=None, block_id=None, *args, **kwargs):
        super().__init__(block_id=block_id, *args, **kwargs)
        # Additional initialization for KmsPractiTest
        self.ENVIRONMENT = more_data['environment']
        self.BROWSER = more_data['browser']
        self.UPDATE_HOST_FILE = more_data['update_host_file']
        self.EXECUTE_AT_NIGHT = more_data['execute_at_night']
        self.VERIFY_VERSIONS = more_data['verify_versions']
        self.KMS_BUILD = more_data['kmsBuild']
        self.PLAYER_VERSION = more_data['playerVersion']
        self.ASSIGNED_TO = more_data['assigned_to']
        self.AUTOMATION_ARGUMENTS = more_data['automation_arguments']
        self.PARTNER = more_data['partner']
        self.BASE_URL = more_data['base_url']
        self.ADMIN_USERNAME = more_data['admin_username']
        self.ADMIN_PASSWORD = more_data['admin_password']
        self.LOGIN_USERNAME = more_data['login_username']
        self.LOGIN_PASSWORD = more_data['login_password']
        self.PLAYER_VERSION_V7 = more_data['playerVersionV7']

    # Add any methods specific to KmsPractiTest here
    def start_service(self):
        if super().is_to_trigger():
            tests_to_execute = self.trigger_execution()
            self.push_to_sqs(tests_to_execute)
            # self.log('DEBUG: Done')
            sleep(10)
        else:
            self.log(f"no sets found under filter id")

    def trigger_execution(self):
        try:
            self.log(f"Execution Triggered")
            filter_test_sets = self.get_all_testsets_under_filter(self.PRACTITEST_TRIGGER_FILTER_ID_LIST)
            initial_tests_list = super().create_tests_json(filter_test_sets)
            if not initial_tests_list:
                raise
            for test_set in filter_test_sets:
                try:
                    test_set_attributes = test_set['attributes']
                    test_set_custom_fields = test_set['attributes']['custom-fields']
                    tests = self.get_list_of_tests_by_status(test_set, test_set_custom_fields[self.PRACTITEST_AUTOMATION_RUN_ONLY])
                    for test in tests:
                        test_attributes = test['attributes']
                        test_custom_fields = test['attributes']['custom-fields']
                        for initial_test in initial_tests_list:
                            if str(initial_test['test_id']) == str(test_attributes['test-display-id']):
                                initial_test['environment'] = try_to_get_from_dict(test_set_custom_fields, self.ENVIRONMENT)
                                initial_test['browser'] = self.get_prioritized_value(self.BROWSER, test_set, test, is_boolean=True)
                                initial_test['update_host_file'] = try_to_get_from_dict(test_set_custom_fields, self.UPDATE_HOST_FILE, is_boolean=True)
                                initial_test['execute_at_night'] = try_to_get_from_dict(test_set_custom_fields, self.EXECUTE_AT_NIGHT, is_boolean=True)
                                initial_test['verify_versions'] = try_to_get_from_dict(test_set_custom_fields,self.VERIFY_VERSIONS, is_boolean=True)
                                initial_test['kmsBuild'] = try_to_get_from_dict(test_set_custom_fields, self.KMS_BUILD)
                                initial_test['playerVersion'] = try_to_get_from_dict(test_set_custom_fields, self.PLAYER_VERSION)
                                initial_test['assigned_to'] = try_to_get_from_dict(test_set_attributes ,self.ASSIGNED_TO)
                                initial_test['automation_arguments'] = try_to_get_from_dict(test_set_custom_fields, self.AUTOMATION_ARGUMENTS, default_value='')
                                initial_test['partner'] = try_to_get_from_dict(test_set_custom_fields, self.PARTNER, default_value='')
                                initial_test['base_url'] = try_to_get_from_dict(test_set_custom_fields, self.BASE_URL, default_value='')
                                initial_test['admin_username'] =  try_to_get_from_dict(test_custom_fields, self.ADMIN_USERNAME, default_value='')
                                initial_test['admin_password'] =  try_to_get_from_dict(test_custom_fields, self.ADMIN_PASSWORD, default_value='')
                                initial_test['login_username'] =  try_to_get_from_dict(test_custom_fields, self.LOGIN_USERNAME, default_value='')
                                initial_test['login_password'] =  try_to_get_from_dict(test_custom_fields, self.LOGIN_PASSWORD, default_value='')
                                initial_test['playerVersionV7'] =  try_to_get_from_dict(test_custom_fields, self.PLAYER_VERSION_V7, default_value='')
                except:
                    self.log(f'Error: failed to parse test set/ test attributes')
        except:
            self.log(f"Error: failed to trigger execution, skipping this execution")
        return initial_tests_list