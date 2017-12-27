# *-* coding: utf-8 *-*

import subprocess
import urllib
import json
import platform
import os
import requests


HOST = 'ip-172-31-10-121'
TASK_GET_URL = 'http://ecsv.org.ua:8001/task/get?hostname=' + HOST
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TASK_WEBHOOK_FINISH = 'http://converter.ecsv.org.ua/webhook/video/accept'
TASK_MANAGER_FINISH = 'http://ecsv.org.ua:8001/webhook/vm/shutdown'

output = json.load(urllib.urlopen(TASK_GET_URL))
filename, file_extension = os.path.splitext(output.get('file_url'))
task_id = output.get('id')
queue_id = output.get('queue_id')

videoFile = urllib.urlopen(output.get('file_url'))
path = BASE_PATH + '/videos/' + str(task_id) + file_extension
with open(path, 'wb') as output:
    output.write(videoFile.read())

output_file_name = str(task_id) + '.mp4'
output_base_path = BASE_PATH + '/videos/converted_'
output_file_path =  output_base_path + output_file_name

command = "ffmpeg -i %s -c:v libx264 -crf 19 -preset:v superfast -c:a aac -b:a 128k -ac 2 -threads 0 -r 10 -strict -2 %s" % (path, output_file_path)
os.system(command)

response = requests.post(TASK_WEBHOOK_FINISH,
                         files={
                             'full': open(output_file_path),
                             'part1': open(output_file_path),
                             'part2': open(output_file_path)
                         },
                         data={'queue_id': queue_id}
                         )
json_response = response.text

response = requests.post(TASK_MANAGER_FINISH,
                         data={'hostname': HOST}
                         )




