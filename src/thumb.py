import subprocess
import requests
from settings import Settings

class Thumb:

    def __init__(self, videoPath, thumbOutput, queueId, extension):
        self.settings = Settings()
        if extension == '.dav':
            thumbCommand = "ffmpeg -i %s %s" % (videoPath, thumbOutput)
        else:
            thumbCommand = "ffmpeg -ss 5 -i %s -vframes 1 -vcodec png -an -y %s" % (videoPath, thumbOutput)
        self.output = subprocess.Popen(thumbCommand, shell=True, stdout=subprocess.PIPE).stdout.read()
        self.thumbVideoData = requests.post(self.settings.getKey('TASK_WEBHOOK_THUMB_VIDEO') + '/' + queueId,
                         files={'full': open(thumbOutput)},
                         )