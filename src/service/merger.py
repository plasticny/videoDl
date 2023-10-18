from service.commandUtils import runCommand, FFMPEG_EXEC

def merge (videoPath:str, audioPath:str, outputDir:str, videoFormat='copy') :
  runCommand(
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
        
      outputDir
    ]
  )
