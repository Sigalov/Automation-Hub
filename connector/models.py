from django.db import models

class Block(models.Model):
    status = models.CharField(max_length=255, default='NOT RUNNING')
    is_running = models.BooleanField(default=False)
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