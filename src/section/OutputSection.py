from enum import Enum
import sys
import tkinter.filedialog as tkFileDialog

from section.Section import Section
from service.YtDlpHelper import Opts

class Message(Enum):
  DIR_SECTION_TITLE = '-- Output directory'
  NAME_SECTION_TITLE = '-- Output file name'

  INVALID_DIR = 'Invalid output directory, select again'
  OUT_DIR = 'Output directory: '

  ENTER_NAME = 'Enter the output file name: (auto) '

class OutputSection (Section):
  def run(self, opts_ls:list[Opts], askDir:bool=True, askName:bool=True) -> list[Opts]:
    for opts in opts_ls:
      opts = opts.copy()
    return super().run(self.__main, opts_ls=opts_ls, askDir=askDir, askName=askName)
  
  def __main(self, opts_ls:list[Opts], askDir:bool=True, askName:bool=True) -> list[Opts]:
    if askDir:
      print(Message.DIR_SECTION_TITLE.value)
      outputDir = self.__askOutputDir()
      for opts in opts_ls:
        opts.outputDir = outputDir

    if askName:
      print(Message.NAME_SECTION_TITLE.value)
      outputName = self.__askOutputName()
      for opts in opts_ls:
        opts.outputName = outputName

    return opts_ls

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
  
  def __askOutputName(self) -> str:
    sys.stdout.flush()
    outputName = input(Message.ENTER_NAME.value)
    return outputName if outputName != '' else None