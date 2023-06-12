from section.Section import Section
import tkinter.filedialog as tkFileDialog
from dlConfig import dlConfig

class SetUpDownloadSection(Section):
  def __init__(self, title):
    super().__init__(title)
    self.config = dlConfig()
    
  def run(self) -> dlConfig:
    return super().run(self.__main)
  
  def __main(self):    
    # ask about subtitle
    print('## Subtitle')
    self.__askSubTitle()
    print('')
    
    # format
    print('## Format')
    self.__askFormat()
    print('')

    # output directory
    print('## Output directory')
    self.__askOutputDir()
    print('')
    
    return self.config
    
  def __askSubTitle (self):
    # subtitle language
    self.config.subLang = input("Enter the language of subtitle:(auto) ")
    
    # write auto subtitle
    doWriteAutoSub = input("Wirte the auto subtitle?:(N) ").upper()
    self.config.doWriteAutoSub = doWriteAutoSub != ''
      
  def __askFormat (self):
    fo = input("Enter the format:(auto) ").lower()
    self.config.outputFormat = 'mp4' if fo == 'auto' or fo == '' else fo
      
  def __askOutputDir (self):
    outputDir = None
    while outputDir == None:  
      dir = tkFileDialog.askdirectory()
      if len(dir) > 0:
        outputDir = dir
        break
      print("Invalid output directory, select again")
    print(f"Output directory {outputDir}")
    
    self.config.outputDir = outputDir
