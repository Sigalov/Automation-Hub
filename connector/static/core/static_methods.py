import json, requests
from retrying import retry

WAIT_EXPONENTIAL_MULTIPLIER = 10000
WAIT_EXPONENTIAL_MAX = 60000


@staticmethod
@retry(wait_exponential_multiplier=WAIT_EXPONENTIAL_MULTIPLIER, wait_exponential_max=WAIT_EXPONENTIAL_MAX)
def send_request(method, url, headers, data=''):
    """Sends a GET/POST/PUT request.
    :param method: 'post' or 'get' or 'put' string
    :param url: URL as string
    :param headers: json as string
    :param data: data/json as string if sending 'post' or 'put' request
    :return: response
    """
    method = str(method).lower()
    try:
        if method == 'get':
            r = requests.get(url, headers=headers, verify=False)
        elif method == 'post':
            r = requests.post(url, headers=headers, data=data, verify=False)
        elif method == 'put':
            r = requests.put(url, headers=headers, data=data, verify=False)
        else:
            print(f'Unknown request method: {method}')
            return
    except requests.exceptions.RequestException:
        raise Exception("WARNING: Failed to send request, going to retry")
    return r


class ImmediateExitException(Exception):
    pass

def not_immediate_exit(exception):
    """Return True for exceptions that are not ImmediateExitException."""
    return not isinstance(exception, ImmediateExitException)


@staticmethod
@retry(retry_on_exception=not_immediate_exit, wait_exponential_multiplier=WAIT_EXPONENTIAL_MULTIPLIER, wait_exponential_max=WAIT_EXPONENTIAL_MAX)
def wait_for_request_200(method, url, headers, msg_on_retry, data=''):
    """Sends a GET/POST/PUT request and verify code 200, else retry.
    :param method: 'post' or 'get' or 'put' string
    :param url: URL as string
    :param headers: json as string
    :param msg_on_retry: msg printed upon fail
    :param data: data/json as string if sending 'post' or 'put' request
    :return: response
    """
    r = send_request(method, url, headers, data)
    if r.status_code == 200:
        return r
    elif r.status_code >= 400:
        try:
            error_data = json.loads(r.text)
            error_message = error_data["errors"][0]["title"]
            raise ImmediateExitException(error_message)
        except json.JSONDecodeError:
            raise ImmediateExitException("Failed to parse error message from server response.")
        except KeyError:
            raise ImmediateExitException("Unexpected error format.")
    else:
        raise Exception('WARNING: ' + str(msg_on_retry) + f'; status code: {r.status_code}')


@staticmethod
def json_find_item(obj, key):
    """
    Recursively searches for a key in a nested dictionary or list and returns its value.

    :param obj: The dictionary or list to search within.
    :param key: The key to search for.
    :return: The value associated with the given key, or None if the key is not found.
    """
    try:
        if key in obj: return obj[key]
        for k, v in obj.items():
            if isinstance(v, dict):
                item = json_find_item(v, key)
                if item is not None:
                    return str(item)
    except Exception:
        print(f'WARNING: Key {str(key)} not found in json file')
        return None


@staticmethod
def load_json_config(json_path):
    """
    Loads a JSON configuration from the specified file path.

    :param json_path: Path to the JSON file to be loaded.
    :return: Dictionary containing the loaded JSON data.

    Raises:
        Exception: If there's an issue reading the file or parsing the JSON, an error message is printed and the program exits with code 1.
    """
    try:
        with open(json_path) as f:
            return json.load(f)
    except Exception:
        print(f'Failed to read json from {json_path}')
        exit(1)


@staticmethod
def get_dict_data_if_not_empty(dictionary):
    """
    Extracts the "data" key from a dictionary if it's not empty.

    :param dictionary: The input dictionary from which to extract data.
    :return: The value associated with the "data" key if it's not empty, otherwise None.
    """
    if len(dictionary["data"]) != 0:
        return dictionary["data"]
    else:
        return


@staticmethod
def create_data_for_test_set_multiple_custom_fields(custom_fields_dict):
    """Creates generic data for updating multiple custom fields in test set by sending one request
    :param custom_fields_dict:
    :return: data as json string
    """
    template_suffix = '}}}}'
    data = '{"data": { "type": "sets", "attributes": {"custom-fields": {'

    for custom_field in custom_fields_dict:
        if type(custom_fields_dict[custom_field]) is list:
            data = data + '"' + str(custom_field) + '": ' + str(custom_fields_dict[custom_field])
        else:
            data = data + '"' + str(custom_field) + '": "' + str(custom_fields_dict[custom_field]) + '"'
        # if not last, add ',' at the end
        if custom_field != list(custom_fields_dict.keys())[-1]:
            data = data + ','
    data = data + template_suffix
    return data


@staticmethod
def safe_len(obj):
    """
    Safely retrieves the length of an object, returning 0 if the object is None.

    :param obj: The object whose length is to be determined.
    :return: Length of the object, or 0 if the object is None.
    """
    return len(obj) if obj is not None else 0


@staticmethod
def load_data_from_json(json_path):
    """Load data from a JSON file and return as a dictionary."""
    try:
        with open(json_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file {json_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {json_path} does not contain valid JSON.")
        return None


@staticmethod
def dict_to_single_line_json(data_dict):
    """
    Converts a given dictionary to a single-line JSON string.

    Parameters:
    - data_dict (dict): The dictionary to be converted.

    Returns:
    - str: Single-line JSON string representation of the dictionary.
    """
    return json.dumps(data_dict)


@staticmethod
def try_to_get_from_dict(dictionary, key, default_value='None', is_boolean=False):
    """
    Attempts to retrieve a value from a dictionary based on the provided key. Returns a default value if the key is not found.

    :param dictionary: The dictionary to search within.
    :param key: The key to search for.
    :param default_value: Value to return if the key is not found (default is 'None').
    :param is_boolean: Flag indicating if the value should be converted to a boolean representation ('yes' to 'true', 'no' to 'false').
    :return: The value associated with the key, or the default value if the key is not found.
    """
    try:
        val = dictionary[key]
        # Handle boolean conversion
        if is_boolean:
            if val == 'yes':
                return 'true'
            elif val == 'no':
                return 'false'
        return str(val)
    except:
        return default_value

@staticmethod
def write_dict_to_json_file(data_dict, filename):
    """
    Write a dictionary to a JSON file.

    :param data_dict: Dictionary to be written.
    :param filename: Name of the file to write to.
    """
    with open(filename, 'w') as f:
        json.dump(data_dict, f, indent=2)
