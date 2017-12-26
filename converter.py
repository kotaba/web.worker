# *-* coding: utf-8 *-*

import ffmpeg
import urllib
import json
import platform
import os
import requests


HOST = HOST
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
stream = ffmpeg.input(path)
stream = ffmpeg.output(stream, output_file_path)
ffmpeg.run(stream)

'''parts = [1,2,3,4,5]

START_FRAME = 0
END_FRAME = 60
for partial in parts:
    part = ffmpeg.input(output_file_path)
    part.trim(start_frame=START_FRAME, end_frame=END_FRAME)
    part = ffmpeg.output(part, output_base_path + 'split_part_' + str(partial) + '_' + output_file_name)
    ffmpeg.run(part)
    START_FRAME = START_FRAME + 60
    END_FRAME = END_FRAME + 60'''

response = requests.post(TASK_WEBHOOK_FINISH,
                         files={
                             'full': open(output_file_path),
                             'part1': open(output_file_path),
                             'part2': open(output_file_path)
                         },
                         data={'queue_id': queue_id}
                         )
json_response = response.text
print json_response

response = requests.post(TASK_MANAGER_FINISH,
                         data={'hostname': HOST}
                         )
print response.text()




