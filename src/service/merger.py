from subprocess import call as subCall

def merge (video, audio, outputDir, videoFormat='copy') :
  cmd_command = f"ffmpeg -i {video} -i {audio} -c:v {videoFormat} -c:a aac {outputDir}"
  print(cmd_command)
  subCall(cmd_command, shell=True)