# *-* coding: utf-8 *-*

from settings import Settings
import json
import urllib
import os

class Task:
    def __init__(self):
        self.settings = Settings()
        self.task_url = self.settings.getKey('TASK_GET_URL')
        self.task_output = json.load(urllib.urlopen(self.task_url))

    def getFileData(self):
        filename, extension = os.path.splitext(self.task_output.get('file_url'))
        return {
            'filename': filename,
            'extension': extension
        }

    def getTaskId(self):
        return self.task_output.get('id')

    def getQueueId(self):
        return self.task_output.get('queue_id')

    def getFileUrl(self):
        return self.task_output.get('file_url')
