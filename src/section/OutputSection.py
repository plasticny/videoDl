from tkinter import filedialog as tkFileDialog
from typing import TypedDict

from src.section.Section import Section


class TOutputSectionRet (TypedDict):
  dir: str
  name: str


class OutputSection (Section):
  def run(self, askDir:bool=True, askName:bool=True) -> TOutputSectionRet:
    return super().run(self.__main, askDir=askDir, askName=askName)
  
  def __main(self, askDir:bool=True, askName:bool=True) -> TOutputSectionRet:
    if askDir:
      print('-- Output directory')
      outputDir = self.__askOutputDir()
    else:
      outputDir = None

    if askName:
      print('-- Output file name')
      outputName = self.__askOutputName()
    else:
      outputName = None

    res : TOutputSectionRet = {
      'dir': outputDir,
      'name': outputName
    }
    return res

  def __askOutputDir(self):
    outputDir = None

    while outputDir == None:  
      dir = tkFileDialog.askdirectory()
      if len(dir) > 0:
        outputDir = dir
        break
      print('Invalid output directory, select again')
    print(f"Output directory: {outputDir}")

    return outputDir
  
  def __askOutputName(self):
    outputName = input('Enter the output file name: (auto) ')
    return outputName if outputName != '' else None