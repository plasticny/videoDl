from enum import Enum

from service.commandUtils import runCommand, FFMPEG_EXEC

class Message (Enum):
  MERGE_FAILED = 'Merge failed'

def merge (videoPath:str, audioPath:str, outputDir:str, videoFormat='copy', quiet=False) :
  retc = runCommand(
    execCommand=FFMPEG_EXEC, 
    paramCommands=[
      '-i',
        videoPath,
        
      '-i',
        audioPath,
        
      '-c:v',
        videoFormat,
        
      '-c:a',
        'aac',
        
      '-c:s',
        'mov_text',
        
      outputDir,

      '-hide_banner -loglevel error' if quiet else ''
    ]
  )

  if retc != 0:
    raise Exception(Message.MERGE_FAILED.value)