# *-* coding: utf-8 *-*

import platform
import os
import re

# Settings class

class Settings:

    def __init__(self):
        self.settingUrl = 'http://vm.cifr.us/settings/get'

        self.settingsData = {
            'HOST': platform.node(),
            'TASK_GET_URL': 'http://vm.cifr.us/task/get?hostname=' + platform.node(),
            'BASE_PATH': os.path.dirname(os.path.abspath(__file__)),
            'TASK_WEBHOOK_FINISH_VIDEO': 'http://vision.cifr.us/webhook/video/accept',
            'TASK_WEBHOOK_FINISH_PART': 'http://vision.cifr.us/webhook/part/accept',
            'TASK_MANAGER_FINISH': 'http://vm.cifr.us/webhook/vm/shutdown',
            'TASK_WEBHOOK_THUMB_VIDEO': 'http://vision.cifr.us/webhook/task/set/thumbnail',
            'length_regexp': 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,',
            're_length': re.compile('Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,')
        }

    # Get settings by key
    def getKey(self, key):
        return self.settingsData.get(key)