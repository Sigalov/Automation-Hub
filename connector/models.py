from django.db import models

class Block(models.Model):
    block_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=255, default='STOPPED')
    running = models.BooleanField(default=False)
    output_data = models.TextField(default='')
    app_name = models.CharField(max_length=255, blank=True, null=True)
    pt_username = models.CharField(max_length=255, blank=True, null=True)
    pt_token = models.CharField(max_length=255, blank=True, null=True)
    aws_access_key = models.CharField(max_length=255, blank=True, null=True)
    aws_secret_key = models.CharField(max_length=255, blank=True, null=True)
    filter_id_list = models.TextField(blank=True, null=True)
    console_output = models.TextField(default="", blank=True)

class LogEntry(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="log_entries")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)