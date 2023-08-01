from section.Section import Section
import tkinter.filedialog as tkFileDialog
from dlConfig import dlConfig

class SetUpDownloadSection(Section):
  def __init__(
      self, title, config:dlConfig, 
      subtitle=True, format=True, outputDir=True, outputName=True, h264=True
    ):
    super().__init__(title)
    self.config = config
    
    self.subtitle = subtitle
    self.format = format
    self.outputDir = outputDir
    self.outputName = outputName
    self.h264 = h264
    
  def run(self) -> dlConfig:
    return super().run(self.__main)
  
  def __main(self):    
    # ask about subtitle
    if self.subtitle:
      print('## Subtitle')
      self.__askSubTitle()
      print('')
    
    # format
    if self.format:
      print('## Format')
      self.__askFormat()
      print('')

    # output directory
    if self.outputDir:
      print('## Output directory')
      self.__askOutputDir()
      print('')
    
    # output name
    if self.outputName:
      print('## Output file name')
      self.__askOutputName()
      print('')
    
    # convert to h.264
    if self.h264:
      print('## H.264')
      self.__askH264()
    
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

  def __askOutputName (self):
    outputName = input('Enter the output file name: (auto) ')
    if outputName == '':
      outputName = None
    
    self.config.outputName = outputName
    
  # ask convert the output to h.264 or not
  def __askH264 (self):
    answer = input('Convert the video to H.264 format? (N) ').upper()
    self.config.h264 = not(answer == 'N' or answer == '')
