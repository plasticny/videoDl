from tkinter import filedialog as tkFileDialog
from typing import TypedDict, Optional
from colorama import Fore, Style

from src.section.Section import Section
from src.service.autofill import get_output_dir_autofill


class TOutputSectionRet (TypedDict):
  dir: Optional[str]
  name: Optional[str]


class OutputSection (Section):
  def run (self, askDir:bool=True, askName:bool=True) -> TOutputSectionRet: # type: ignore
    return super().run(self.__main, askDir=askDir, askName=askName)
  
  def __main(self, askDir:bool=True, askName:bool=True) -> TOutputSectionRet:
    if askDir:
      print('-- Output directory')
      outputDir = self._ask_dir()
    else:
      outputDir = None

    if askName:
      print('-- Output file name')
      outputName = self.__askOutputName()
    else:
      outputName = None

    res: TOutputSectionRet = {
      'dir': outputDir,
      'name': outputName
    }
    return res

  def _ask_dir(self):
    autofill = get_output_dir_autofill()
    
    if autofill is not None:
      print(f'{Fore.GREEN}Output directory autofilled{Style.RESET_ALL}')
      outputDir = autofill
    else:
      while True:
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