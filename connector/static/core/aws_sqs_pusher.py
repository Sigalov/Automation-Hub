import boto3
import json

class SQSPusher:
    def __init__(self, access_key, secret_key, region_name='us-west-2'):
        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )
        self.sqs = self.session.resource('sqs')

    def push_to_queue(self, queue_url, messages):
        """
        Push messages to the SQS queue.

        :param queue_url: URL of the SQS queue.
        :param messages: A single dictionary or a list of dictionaries to be sent as messages.
        :return: List of responses from SQS.
        """
        queue = self.sqs.Queue(queue_url)

        # Ensure messages is a list even if a single message is provided
        if not isinstance(messages, list):
            messages = [messages]

        responses = []

        for i in range(0, len(messages), 10):  # SQS allows a batch of max 10 messages
            batch = messages[i:i + 10]
            entries = [{'Id': str(j), 'MessageBody': json.dumps(msg)} for j, msg in enumerate(batch)]
            response = queue.send_messages(Entries=entries)
            responses.append(response)

        return responses

# Usage
# pusher = SQSPusher('YOUR_ACCESS_KEY', 'YOUR_SECRET_KEY')
# single_message_response = pusher.push_to_queue('YOUR_SQS_QUEUE_URL', {"key": "value"})
# bulk_messages_response = pusher.push_to_queue('YOUR_SQS_QUEUE_URL', [{"key1": "value1"}, {"key2": "value2"}])
# print(single_message_response)
# print(bulk_messages_response)
