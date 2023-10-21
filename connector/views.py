import datetime
import json
from rest_framework.decorators import api_view
from connector.static.core.kms.kms_practitest import KmsPractiTest
import time
from django.db.models import Max
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .static.core import static_methods
from multiprocessing import Process
import os
import django

# Set up the Django settings module for new processes
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connector.settings')

block_processes = {}  # Dictionary to store processes by block_id
block_flags = {}  # Dictionary to store continue_running flags by block_id


def log_message_to_block(block, message):
    from .models import LogEntry
    LogEntry.objects.create(block=block, content=f"[{datetime.datetime.now()}] {message}")


def list_blocks(request):
    from .models import Block
    blocks = Block.objects.all()
    for block in blocks:
        block.console_output = block.console_output.replace("\\n", "\n")
    return render(request, 'list_blocks.html', {'blocks': blocks})


@csrf_exempt
def _run_service_indefinitely(data, block_id, initial_data):
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

        if data['app_name'] == 'kms':
            more_data = static_methods.load_data_from_json("connector/static/core/kms/optional.json")
            instance = KmsPractiTest(more_data, block_id=block_id, **initial_data)
            instance.start_service()
            time.sleep(10)
        else:
            # Use print for now; you might replace it with a more appropriate logging mechanism
            print(f"Block {block_id} started.")
            break


@csrf_exempt
def start_block(request, block_id):
    block_id = int(block_id)
    from .models import Block
    block = Block.objects.get(id=block_id)
    log_message_to_block(block, f"Block {block_id} started.")
    block.status = "RUNNING"
    block.save()

    data = _fetch_and_save_block_data(request, block)
    initial_data = _load_initial_data(data)

    block.is_running = True
    block.save()

    process = Process(target=_run_service_indefinitely, args=(data, block_id, initial_data))
    process.start()
    block_processes[block_id] = process

    return JsonResponse({'status': 'starting...'})


def _fetch_and_save_block_data(request, block):
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
    initial_data = static_methods.load_data_from_json("connector/static/core/initialize.json")
    initial_data["project_name"] = data['app_name']
    initial_data["pt_username"] = data['pt_username']
    initial_data["pt_token"] = data['pt_token']
    initial_data["access_key"] = data['aws_access_key']
    initial_data["secret_key"] = data['aws_secret_key']
    initial_data["filter_id_list"] = data['filter_id_list']
    return initial_data


@csrf_exempt
def stop_block(request, block_id):
    block_id = int(block_id)
    from .models import Block
    block = Block.objects.get(id=block_id)
    block.status = "NOT RUNNING"
    log_message_to_block(block, f"Block {block_id} stopped.")
    block.save()

    if block.is_running:
        block.is_running = False
        block.status = "NOT RUNNING"
        block.save()

    return JsonResponse({"status": "STOPPED"})


@csrf_exempt
def delete_block(request, block_id):
    from .models import Block
    block = Block.objects.get(id=block_id)
    log_message_to_block(block, f"Block {block_id} deleted.")
    block.delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
def create_block(request):
    if request.method == "POST":
        try:
            from .models import Block
            # Using the maximum block ID currently in use and incrementing it for the new block
            max_block_id = Block.objects.all().aggregate(Max('block_id'))
            if max_block_id['block_id__max'] is not None:
                next_block_id = int(max_block_id['block_id__max'][5:]) + 1
            else:
                next_block_id = 1
            block_id_str = f"Block{next_block_id}"
            block = Block(block_id=block_id_str, status="NOT RUNNING", is_running=False)
            block.save()

            return JsonResponse({"message": f"Block {block_id_str} created successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)

def vue_app(request):
    return render(request, 'index.html')


@api_view(['GET'])
def block_list(request):
    from .serializers import BlockSerializer
    from .models import Block
    blocks = Block.objects.all()
    serializer = BlockSerializer(blocks, many=True)
    return JsonResponse(serializer.data, safe=False)