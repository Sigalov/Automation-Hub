import datetime
import json
from rest_framework.decorators import api_view
from connector.static.core.kms.kms_practitest import KmsPractiTest
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .static.core import static_methods
from multiprocessing import Process
import os
import django
from django.db import transaction

# Set up the Django settings module for new processes
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connector.settings')
block_processes = {}  # Dictionary to store processes by ID

def log_message_to_block(block, message):
    """
    Logs a message associated with a specific block.

    :param block: The block object.
    :param message: The message to be logged.
    """
    from .models import LogEntry
    LogEntry.objects.create(block=block, content=f"[{datetime.datetime.now()}] {message}")


def list_blocks(request):
    """
    Renders a page that lists all blocks.

    :param request: The HTTP request object.
    :return: Rendered HTML page with a list of blocks.
    """
    from .models import Block
    blocks = Block.objects.all()
    for block in blocks:
        block.console_output = block.console_output.replace("\\n", "\n")
    return render(request, 'list_blocks.html', {'blocks': blocks})


@csrf_exempt
def _run_service_indefinitely(data, block_id, initial_data):
    """
    Runs a service continuously based on specific conditions.

    :param data: Configuration data for the service.
    :param block_id: ID of the associated block.
    :param initial_data: Initial data for the service.
    """
    # Set up Django
    django.setup()
    # Close existing database connections
    from django import db
    db.connections.close_all()
    # Now, you can safely import your models and use Django functionalities
    from .models import Block
    block_id = int(block_id)

    while True:
        # Fetch the block object inside the loop
        block = Block.objects.get(id=block_id)
        if not block.is_running:
            break

        if block.filter_id_list and not block.filter_id_list == 'None':
            initial_data['practitest_trigger_filter_id_list'] = block.filter_id_list

        if data['app_name'] == 'kms':
            more_data = static_methods.load_data_from_json("connector/static/core/kms/optional.json")
            instance = KmsPractiTest(more_data, block_id=block_id, **initial_data)
            instance.start_service()
            time.sleep(10)
        else:
            log_message_to_block(block, f"Unknown Application Name: {data['app_name']}.")
            set_block_status_not_running(block)
            break


@csrf_exempt
def start_block(request, block_id):
    """
    Starts a specified block.

    :param request: The HTTP request object.
    :param block_id: ID of the block to be started.
    """
    block_id = int(block_id)
    from .models import Block
    block = Block.objects.get(id=block_id)
    log_message_to_block(block, f"Starting Service...")

    data = _fetch_and_save_block_data(request, block)
    initial_data = _load_initial_data(data)

    set_block_status_running(block)
    process = Process(target=_run_service_indefinitely, args=(data, block_id, initial_data))
    process.start()
    block_processes[block_id] = process

    return JsonResponse({'status': 'starting...'})


def set_block_status_running(block):
    """
    Updates the status of a block to 'running'.

    :param block: The block object.
    """
    block.status = "RUNNING"
    block.is_running = True
    block.save()


def set_block_status_not_running(block):
    """
    Updates the status of a block to 'not running'.

    :param block: The block object.
    """
    block.status = "NOT RUNNING"
    block.is_running = False
    block.save()
    log_message_to_block(block, f'Service Stopped')


def _fetch_and_save_block_data(request, block):
    """
    Fetches and saves data associated with a block.

    :param request: Data from the HTTP request.
    :param block: The block object.

    """
    data = json.loads(request.body)
    block.app_name = data['app_name']
    block.pt_username = data['pt_username']
    block.pt_token = data['pt_token']
    block.aws_access_key = data['aws_access_key']
    block.aws_secret_key = data['aws_secret_key']
    block.filter_id_list = data['filter_id_list']
    block.save()
    return data


def _load_initial_data(data):
    """
    Loads initial data from a specified JSON file and updates it with data from the provided dictionary.

    The method reads data from the "connector/static/core/initialize.json" file and then updates specific fields with values from the input dictionary.

    :param data: Dictionary containing key-value pairs to update the loaded data with. Expected keys include 'app_name', 'pt_username', 'pt_token', 'aws_access_key', and 'aws_secret_key'.
    :return: Dictionary containing the merged data from the JSON file and the input dictionary.
    """
    initial_data = static_methods.load_data_from_json("connector/static/core/initialize.json")
    initial_data["project_name"] = data['app_name']
    initial_data["pt_username"] = data['pt_username']
    initial_data["pt_token"] = data['pt_token']
    initial_data["access_key"] = data['aws_access_key']
    initial_data["secret_key"] = data['aws_secret_key']
    return initial_data


@csrf_exempt
def stop_block(request, block_id):
    """
    Stops a specified block.

    :param request: The HTTP request object.
    :param block_id: ID of the block to be stopped.
    """
    block_id = int(block_id)
    from .models import Block
    block = Block.objects.get(id=block_id)
    block.status = "NOT RUNNING"
    block.save()

    if block.is_running:
        set_block_status_not_running(block)

    return JsonResponse({"status": "STOPPED"})


@csrf_exempt
def delete_block(request, block_id):
    """
    Deletes a specified block.

    :param request: The HTTP request object.
    :param block_id: ID of the block to be deleted.
    """
    from .models import Block
    block = Block.objects.get(id=block_id)
    log_message_to_block(block, f"Service {block_id} deleted.")
    block.delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
def create_block(request):
    """
    Creates a new block.

    :param request: The HTTP request object.
    """
    if request.method == "POST":
        try:
            from .models import Block
            with transaction.atomic():
                block = Block(status="NOT RUNNING", is_running=False)
                block.save()

            return JsonResponse({
                "message": "New block created successfully",
                "block": {
                    "id": block.id,
                    "status": block.status,
                    "is_running": block.is_running,
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)


def vue_app(request):
    """
    Renders the main Vue application.

    :param request: The HTTP request object.
    :return: Rendered Vue application.
    """
    return render(request, 'index.html')


@api_view(['GET'])
def block_list(request):
    """
    Retrieves a list of all blocks in a serialized format.

    :param request: The HTTP request object.
    :return: JSON response containing a list of blocks.
    """
    from .serializers import BlockSerializer
    from .models import Block
    blocks = Block.objects.all()
    serializer = BlockSerializer(blocks, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_console_output(request, block_id):
    """
    Fetches the console output associated with a specific block.

    :param request: The HTTP request object.
    :param block_id: ID of the block for which console output is needed.
    """
    from .models import Block
    try:
        block = Block.objects.get(pk=block_id)
        logs = block.log_entries.order_by('-timestamp').values_list('content', flat=True)
        return JsonResponse({'console_output': "\n".join(logs)})
    except Block.DoesNotExist:
        return JsonResponse({'error': 'Block not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)


def get_block_status(request, block_id):
    """
    Retrieves the status of a specified block.

    :param request: The HTTP request object.
    :param block_id: ID of the block whose status is to be retrieved.
    """
    from .models import Block
    try:
        block = Block.objects.get(pk=block_id)
        return JsonResponse({'status': block.status})
    except Block.DoesNotExist:
        return JsonResponse({'error': 'Block not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)
