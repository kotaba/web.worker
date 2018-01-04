# *-* coding: utf-8 *-*

import subprocess
import urllib
import json
import platform
import os
import requests
import re
import math

target_files = {}
part_files = {}
HOST = platform.node()
TASK_GET_URL = 'http://vm.cifr.us/task/get?hostname=' + HOST
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TASK_WEBHOOK_FINISH_VIDEO = 'http://vision.cifr.us/webhook/video/accept'
TASK_WEBHOOK_FINISH_PART = 'http://vision.cifr.us/webhook/part/accept'
TASK_MANAGER_FINISH = 'http://vm.cifr.us/webhook/vm/shutdown'
TASK_WEBHOOK_THUMB_VIDEO = 'http://vision.cifr.us/webhook/task/set/thumbnail'
length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)

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
output_file_path = output_base_path + output_file_name

output_thumb_base_path = BASE_PATH + '/videos/thumb.png'
thumbCommand = "ffmpeg -i %s -r 1  -t 00:00:10 -f image2 %s" % (path, output_thumb_base_path)
output = subprocess.Popen(thumbCommand, shell=True, stdout=subprocess.PIPE).stdout.read()
thumbVideoData = requests.post(TASK_WEBHOOK_THUMB_VIDEO + '/' + queue_id,
                         files=open(output_thumb_base_path),
                         )

command = "ffmpeg -i %s -c:v libx264 -crf 19 -preset:v superfast -c:a aac -b:a 128k -ac 2 -r 10 -strict -2 %s" % (
path, output_file_path)
os.system(command)

target_files['full'] = open(output_file_path)

split_length = 3600
output = subprocess.Popen("ffmpeg -i '" + output_file_path + "' 2>&1 | grep 'Duration'",
                          shell=True,
                          stdout=subprocess.PIPE
                          ).stdout.read()


matches = re_length.search(output)

try:
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
                    int(matches.group(2)) * 60 + \
                    int(matches.group(3))
        print "Video length in seconds: " + str(video_length)
    else:
        print "Can't determine video length."
        raise Exception
    split_count = int(math.ceil(video_length / float(split_length)))
    print split_count
    if split_count > 1:
        split_cmd = "ffmpeg -i '%s' " % output_file_path
        try:
            filebase = ".".join(output_file_path.split(".")[:-1])
            fileext = output_file_path.split(".")[-1]
        except IndexError as e:
            raise IndexError("No . in filename. Error: " + str(e))
        for n in range(0, split_count):
            split_str = ""
            if n == 0:
                split_start = 0
            else:
                split_start = split_length * n

            split_str += " -strict -2 -ss " + str(split_start) + " -t " + str(split_length) + \
                 " '" + filebase + "-" + str(n) + "." + fileext + \
                 "'"
            print "About to run: " + split_cmd + split_str
            output = subprocess.Popen(split_cmd + split_str, shell=True, stdout=
            subprocess.PIPE).stdout.read()
            part_files['part_' + str(n)] = open(filebase + "-" + str(n) + "." + fileext)
except Exception as e:
    print e

finishVideoData = requests.post(TASK_WEBHOOK_FINISH_VIDEO,
                         files=target_files,
                         data={'queue_id': queue_id}
                         )

saved_video_data = finishVideoData.json()

video_id = saved_video_data.get('video_id')

response = requests.post(TASK_WEBHOOK_FINISH_PART,
                         files=part_files,
                         data={'video_id': video_id}
                         )
print response.text

requests.post(TASK_MANAGER_FINISH,
                         data={'hostname': HOST}
                         )
