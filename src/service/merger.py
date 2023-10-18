from subprocess import call as subCall

def merge (video, audio, outputDir, videoFormat='copy') :
  cmd_command = f"ffmpeg -i {video} -i {audio} -c:v {videoFormat} -c:a aac -c:s mov_text {outputDir}"
  subCall(cmd_command, shell=True)