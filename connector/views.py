import datetime
import json
import logging

from rest_framework.decorators import api_view

from connector.static.core.kms.kms_practitest import KmsPractiTest
from .serializers import BlockSerializer
import threading
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Block
from .static.core import static_methods


@csrf_exempt  # To exempt from CSRF checks for demonstration purposes
def add_block(request):
    if request.method == 'POST':
        block_id = request.POST.get('block_id')
        if block_id:
            Block.objects.create(block_id=block_id)
            return redirect('list_blocks')  # Redirect to the list view after adding
    return render(request, 'add_block.html')  # Render the form for adding a block


def list_blocks(request):
    blocks = Block.objects.all()
    return render(request, 'list_blocks.html', {'blocks': blocks})

@csrf_exempt
def start_block(request, block_id):
    block = Block.objects.get(id=block_id)
    block.status = "Starting..."
    block.console_output += f"[{datetime.datetime.now()}] Block {block_id} started.\n"
    block.save()

    # Fetching block parameters from the POST request
    data = json.loads(request.body)
    app_name = data['app_name']
    pt_username = data['pt_username']
    pt_token = data['pt_token']
    aws_access_key = data['aws_access_key']
    aws_secret_key = data['aws_secret_key']
    filter_id_list = data['filter_id_list']

    # Saving these parameters to the block
    block.app_name = app_name
    block.pt_username = pt_username
    block.pt_token = pt_token
    block.aws_access_key = aws_access_key
    block.aws_secret_key = aws_secret_key
    block.filter_id_list = filter_id_list
    block.save()

    initial_data = {}
    initial_data = static_methods.load_data_from_json("connector/static/core/initialize.json")
    initial_data["project_name"] = app_name
    initial_data["pt_username"] = pt_username
    initial_data["pt_token"] = pt_token
    initial_data["access_key"] = aws_access_key
    initial_data["secret_key"] = aws_secret_key
    initial_data["filter_id_list"] = filter_id_list

    if app_name == 'kms':
        # The following line is a placeholder; the actual loading function should be integrated
        more_data = static_methods.load_data_from_json("connector/static/core/kms/optional.json")
        instance = KmsPractiTest(more_data, block=block, **initial_data)
        instance.start_service()  # This line assumes the KmsPractiTest class has been imported and defined
    else:
        block.console_output += f"[{datetime.datetime.now()}] Block {block_id} started.\n"
        block.save()

    return JsonResponse({'status': 'starting...'})


@csrf_exempt
def stop_block(request, block_id):
    block = Block.objects.get(id=block_id)
    block.status = "Stopping..."
    block.console_output += f"[{datetime.datetime.now()}] Block {block_id} stopped.\n"
    block.save()

    # Simulating some background process using threading
    threading.Thread(target=dummy_block_stop_service, args=(block,)).start()
    return JsonResponse({'status': 'success'})


# Simulating service logic for demonstration purposes
def dummy_block_start_service(block):
    time.sleep(5)  # Simulating some process that takes 5 seconds
    block.status = "Started"
    block.save()


def dummy_block_stop_service(block):
    time.sleep(5)  # Simulating some process that takes 5 seconds
    block.status = "Stopped"
    block.save()


# Integrate the starting logic into the start_service view
def start_service(request, block_id):
    block = Block.objects.filter(block_id=block_id).first()
    if not block:
        return JsonResponse({"message": "Block ID not found."}, status=404)

    block.status = "RUNNING"
    block.running = True
    block.save()

    # Use threading to simulate the service running in the background
    t = threading.Thread(target=dummy_block_start_service, args=(block,))
    t.start()

    return JsonResponse({"message": f"Service started for {block_id}"})


# Integrate the stopping logic into the stop_service view
def stop_service(request, block_id):
    block = Block.objects.filter(block_id=block_id).first()
    if not block:
        return JsonResponse({"message": "Block ID not found."}, status=404)

    block.running = False
    block.save()

    # The actual logic to stop the service would be here
    # In this dummy example, we just set the running attribute to False and wait for the thread to finish

    block.status = "STOPPED"
    block.save()

    return JsonResponse({"message": f"Service stopped for {block_id}"})


def get_status(request, block_id):
    block = Block.objects.filter(block_id=block_id).first()
    if not block:
        return JsonResponse({"message": "Block ID not found."}, status=404)

    if block.running:
        return JsonResponse({"status": "RUNNING"})
    return JsonResponse({"status": "STOPPED"})


@csrf_exempt
def delete_block(request, block_id):
    block = Block.objects.get(id=block_id)
    block.console_output += f"[{datetime.datetime.now()}] Block {block_id} deleted.\n"
    block.delete()
    return JsonResponse({'status': 'success'})


@csrf_exempt
def create_block(request):
    if request.method == "POST":
        try:
            # Get the current count of blocks and add one for the new block's ID
            current_count = Block.objects.count()
            block_id = f"Block{current_count + 1}"

            # Check if block with this ID already exists (just to be extra safe)
            while Block.objects.filter(block_id=block_id).exists():
                current_count += 1
                block_id = f"Block{current_count + 1}"

            block = Block(block_id=block_id, status="stopped")
            block.save()
            return JsonResponse({"message": f"Block {block_id} created successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=405)


def vue_app(request):
    return render(request, 'index.html')

def get_console_output(request, block_id):
    block = Block.objects.get(pk=block_id)
    return JsonResponse({'console_output': block.console_output})

@api_view(['GET'])
def block_list(request):
    blocks = Block.objects.all()
    serializer = BlockSerializer(blocks, many=True)
    return JsonResponse(serializer.data, safe=False)

def log_to_block_console(block_id, message):
    """
    Append a message to the block's console output.
    """
    try:
        block = Block.objects.get(id=block_id)
        block.console_output += f"[{datetime.datetime.now()}] {message}\n"
        block.save()
    except Block.DoesNotExist:
        pass  # If the block does not exist, simply pass.