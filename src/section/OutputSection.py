from enum import Enum
import sys
import tkinter.filedialog as tkFileDialog

from section.Section import Section
from dlConfig import DefaultConfig

class Message(Enum):
  DIR_SECTION_TITLE = '-- Output directory'
  NAME_SECTION_TITLE = '-- Output file name'

  INVALID_DIR = 'Invalid output directory, select again'
  OUT_DIR = 'Output directory: '

  ENTER_NAME = 'Enter the output file name: (auto) '

class OutputSection (Section):
  def __init__(
      self, title, 
      askDir:bool=True, askName:bool=True
    ):
    super().__init__(title)
    self.askDir = askDir
    self.askName = askName

  # RETURN: (outputDir, outputName)
  def run(self) -> (str, str):
    return super().run(self.__main)
  
  def __main(self) -> (str, str):
    if self.askDir:
      print(Message.DIR_SECTION_TITLE.value)
      outputDir = self.__askOutputDir() 
    else:
      outputDir = DefaultConfig.outputDir.value

    if self.askName:
      print(Message.NAME_SECTION_TITLE.value)
      outputName = self.__askOutputName()
    else:
      outputName = DefaultConfig.outputName.value

    return (outputDir, outputName)

  def __askOutputDir(self):
    outputDir = None

    while outputDir == None:  
      dir = tkFileDialog.askdirectory()
      if len(dir) > 0:
        outputDir = dir
        break
      print(Message.INVALID_DIR.value)
    print(f"{Message.OUT_DIR.value} {outputDir}")

    return outputDir
  
  def __askOutputName(self):
    sys.stdout.flush()
    outputName = input(Message.ENTER_NAME.value)
    if outputName == '':
      outputName = DefaultConfig.outputName.value
    return outputName