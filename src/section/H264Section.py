from section.Section import Section
from service.commandUtils import runCommand, FFMPEG_EXEC
from dlConfig import dlConfig

from time import time
from os import rename, remove

# ask the login cookie
class H264Section(Section):
  def __init__(self, title, config:dlConfig):
    super().__init__(title)
    self.config = config
    
  def run(self):
    return super().run(self.__convert)
  
  def __convert(self):
    inFileWholePath = f'{self.config.outputDir}/{self.config.getFileName()}.{self.config.outputExt}'
    outFileWholePath = f'{self.config.outputDir}/{int(time())}.mp4'
    
    runCommand(
      execCommand=FFMPEG_EXEC, 
      paramCommands=[
        '-i',
          inFileWholePath,
          
        '-c:v',
          'libx264',
          
        '-c:a',
          'copy',
          
        outFileWholePath
      ]
    )
    
    remove(inFileWholePath)
    rename(outFileWholePath, inFileWholePath)