import subprocess
import math

class Splitter:
    def __init__(self, matches, split_length, output_file_path):
        self.part_files = {}
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
                    self.part_files['part_' + str(n)] = open(filebase + "-" + str(n) + "." + fileext)
        except Exception as e:
            print e

    def getPartFiles(self):
        return self.part_files