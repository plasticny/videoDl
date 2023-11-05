from service.merger import merge
from service.urlHelper import getSource, UrlSource
from service.MetaData import MetaData, VideoMetaData
from service.YtDlpHelper import Opts

from os import remove, rename
from uuid import uuid4

from section.Section import Section, HeaderType
from section.UrlSection import UrlSection
from section.DownloadSection import DownloadSection
from section.ListSubtitleSection import ListSubtitleSection
from section.LoginSection import LoginSection
from section.SubTitleSection import SubTitleSection
from section.OutputSection import OutputSection

class lazyYtDownload:
  def __init__(self) -> None:
    self.opts = Opts()

  def run (self, loop=True):
    print("----------------- Downlaod -----------------", end='\n\n')

    while True:
      url = UrlSection(title='Url').run()

      self.opts = self.configDownload(url)

      md = MetaData.fetchMetaData(url)
      
      # check the number of video need to download
      videos : list[VideoMetaData] = []
      if md.isPlaylist():
        videos.extend(md.getVideos())
      else:
        videos.append(md)
      print(f'Video found: {len(videos)}')

      # download
      for idx, v in enumerate(videos):
        Section(title=f'Video {idx+1} of {len(videos)}').run(
          self.download, 
          title=v.title, url=v.url
        )

      if not loop:
        break
    return

  def configDownload(self, url) -> Opts:
    # ask login    
    self.login(url)

    # list subtitle
    ListSubtitleSection(title='List Subtitle').run(url, self.opts)

    # set up download
    # subtitle, output dir
    self.opts = Section(title='Set up download').run(self.setup)

    return self.opts
  
  def login(self, url:str):
    # ask login if bilibili
    if getSource(url) == UrlSource.BILIBILI:
      return LoginSection(title='Login').run(self.opts)
    return None

  def setup(self) -> Opts:
    # subtitle
    self.opts = SubTitleSection(
      title='Subtitle',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(self.opts)

    # output dir
    self.opts = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(self.opts, askName=False)

    return self.opts

  def download(self, title, url):
    # set a random output name
    fileNm = uuid4().__str__()

    # download video
    self.opts.format("bv*[ext=mp4]").outputName(fileNm+'.mp4')
    DownloadSection(
      title="Downloading video",
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(url, self.opts, retry=2)

    # download audio
    self.opts.format("ba*[ext=m4a]").outputName(fileNm+'.m4a')
    DownloadSection(
      title="Downloading audio",
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(url, self.opts, retry=2)

    # merge
    optsObj = self.opts()
    filePath = f'{optsObj["paths"]["home"]}/{fileNm}'
    videoFilePath = f'{filePath}.mp4'
    audioFilePath = f'{filePath}.m4a'
    mergeFilePath = f'{filePath}_merge.mp4'
    Section(title="Merging").run(
      bodyFunc=merge, 
      videoPath=videoFilePath, 
      audioPath=audioFilePath, 
      outputDir=mergeFilePath,
      videoFormat='libx264'
    )

    # remove video and audio file
    remove(videoFilePath)
    remove(audioFilePath)

    # rename the output file
    rename(mergeFilePath, f'{optsObj["paths"]["home"]}/{title}.mp4')

    return

if __name__ == "__main__":
  lazyYtDownload().run()