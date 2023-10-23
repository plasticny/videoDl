from section.Section import Section, HeaderType
from section.SubTitleSection import SubTitleSection
from section.FormatSection import FormatSection
from section.OutputSection import OutputSection
from dlConfig import dlConfig

class SetUpDownloadSection(Section):
  def __init__(
      self, title, config:dlConfig, 
      subtitle=True, format=True, outputDir=True, outputName=True
    ):
    super().__init__(title)
    self.config = config
    
    self.subtitle = subtitle
    
    self.format = format

    self.outputDir = outputDir
    self.outputName = outputName
    
  def run(self) -> dlConfig:
    return super().run(self.__main)
  
  def __main(self):    
    # ask about subtitle
    if self.subtitle:
      subSection = SubTitleSection('SubTitle')
      subSection.headerType = HeaderType.SUB_HEADER

      lang, doWriteAutoSub = subSection.run()

      self.config.subLang = lang
      self.config.doWriteAutoSub = doWriteAutoSub
    
    # format
    if self.format:
      formatSection = FormatSection('Format')
      formatSection.headerType = HeaderType.SUB_HEADER
      self.config.outputFormat = formatSection.run()

    # output directory & output name
    if self.outputName or self.outputDir:
      outSection = OutputSection(
        title='Output',
        askDir=self.outputDir,
        askName=self.outputName,
      )
      outSection.headerType = HeaderType.SUB_HEADER
      outputDir, outputName = outSection.run()

      self.config.outputDir = outputDir
      self.config.outputName = outputName
    
    return self.config
