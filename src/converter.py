import urllib
from settings import Settings
from thumb import Thumb
import os
import subprocess
import re
from split import Splitter
import requests

class Converter:

    def __init__(self, fileUrl, taskId, extension, queueId):
        self.settings = Settings()
        self.videoFile = urllib.urlopen(fileUrl)
        self.BASE_PATH = self.settings.getKey('BASE_PATH')
        self.taskId = taskId
        self.queueId = queueId
        self.extension = extension

        self.downloadFile(target_path=self.getSavePath())
        self.outputPaths = self.getOutputPath()

        self.splitSeconds = 3600

        self.targetFiles = {}
        self.partFiles = {}

        self.thumb = Thumb(
            videoPath=self.getSavePath(),
            thumbOutput=self.getOutputPath().get('output_thumb_path'),
            queueId=self.queueId
        )

        if self.extension == '.mp4' or self.extension == '.avi':
            self.convertStandartModule()
        elif self.extension == '.mov':
            self.convertMovModule()

        self.splitter = Splitter(matches=self.getDuration(), split_length=self.splitSeconds, output_file_path=self.getOutputPath().get('output_file_path'))
        self.partFiles = self.splitter.getPartFiles()

        if self.targetFiles:

            finishVideoData = requests.post(self.settings.getKey('TASK_WEBHOOK_FINISH_VIDEO'),
                         files=self.targetFiles,
                         data={'queue_id': self.queueId}
                         )

            saved_video_data = finishVideoData.json()
            video_id = saved_video_data.get('video_id')

            if self.partFiles:
                requests.post(self.settings.getKey('TASK_WEBHOOK_FINISH_PART'),
                            files=self.partFiles,
                            data={'video_id': video_id}
                            )

            requests.post(self.settings.getKey('TASK_MANAGER_FINISH'),
                         data={'hostname': self.settings.getKey('HOST')}
                         )

    def getSavePath(self):
        return self.BASE_PATH + '/videos/' + str(self.taskId) + self.extension

    def downloadFile(self, target_path):
        with open(target_path, 'wb') as output:
            output.write(self.videoFile.read())

    def getOutputPath(self):
        outputFileName = str(self.taskId) + '.mp4'
        outputBasePath = self.BASE_PATH + '/videos/converted_'
        outputFilePath = outputBasePath + outputFileName
        output_thumb_path = self.BASE_PATH + '/videos/thumb.png'

        return {
            'output_file_path':  outputFilePath,
            'output_thumb_path': output_thumb_path
        }

    # if convert mp4 or avi
    def convertStandartModule(self):
        command = "ffmpeg -i %s -c:v libx264 -crf 19 -preset:v superfast -c:a aac -b:a 128k -ac 2 -r 10 -strict -2 %s" % (self.getSavePath(), self.getOutputPath().get('output_file_path'))
        os.system(command)
        self.targetFiles['full'] = open(self.getOutputPath().get('output_file_path'))

    def convertMovModule(self):
        command = "ffmpeg -i %s -c copy -preset:v superfast -b:a 128k -strict -2 %s" % (self.getSavePath(), self.getOutputPath().get('output_file_path'))
        os.system(command)
        self.targetFiles['full'] = open(self.getOutputPath().get('output_file_path'))

    def getDuration(self):
        output = subprocess.Popen("ffmpeg -i '" + self.getOutputPath().get('output_file_path') + "' 2>&1 | grep 'Duration'",
                          shell=True,
                          stdout=subprocess.PIPE
                          ).stdout.read()
        matches = self.settings.getKey('re_length').search(output)

        return matches