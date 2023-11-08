import service.packageChecker as packageChecker
packageChecker.check()

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
  def run (self, loop=True):
    print("----------------- Downlaod -----------------", end='\n\n')

    while True:
      opts = Opts()

      url = UrlSection(title='Url').run()

      opts = self.configDownload(url, opts)

      # check the number of video need to download
      md = MetaData.fetchMetaData(url)
      videos : list[VideoMetaData] = []
      if md.isPlaylist():
        videos.extend(md.getVideos())
      else:
        videos.append(md)

      # download
      for idx, v in enumerate(videos):
        Section(title=f'Video {idx+1} of {len(videos)}').run(
          self.download, opts=opts,
          title=v.title, url=v.url
        )

      if not loop:
        break
    return

  def configDownload(self, url, opts) -> Opts:
    # ask login    
    opts = self.login(url, opts=opts)

    # list subtitle
    ListSubtitleSection(title='List Subtitle').run(url, opts)

    # set up download
    # subtitle, output dir
    opts = Section(title='Set up download').run(self.setup, opts=opts)

    return opts
  
  def login(self, url:str, opts:Opts) -> Opts:
    # ask login if bilibili
    if getSource(url) == UrlSource.BILIBILI:
      return LoginSection(title='Login').run(opts)
    return opts

  def setup(self, opts) -> Opts:
    # subtitle
    opts = SubTitleSection(
      title='Subtitle',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts)

    # output dir
    opts = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts, askName=False)

    return opts

  def download(self, opts:Opts, title, url):
    # set a random output name
    fileNm = uuid4().__str__()

    # download video
    opts.format("bv*[ext=mp4]").outputName(fileNm+'.mp4')
    DownloadSection(
      title="Downloading video",
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(url, opts, retry=2)

    # download audio
    opts.format("ba*[ext=m4a]").outputName(fileNm+'.m4a')
    DownloadSection(
      title="Downloading audio",
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(url, opts, retry=2)

    # merge
    optsObj = opts()
    outputDir = optsObj["paths"]["home"]
    videoFileNm = f'{fileNm}.mp4'
    audioFileNm = f'{fileNm}.m4a'
    mergeFileNm = f'{fileNm}_merge.mp4'
    Section(title="Merging").run(
      bodyFunc=merge, 
      videoPath=f"{outputDir}/{videoFileNm}", 
      audioPath=f"{outputDir}/{audioFileNm}",
      outputDir=f"{outputDir}/{mergeFileNm}",
      videoFormat='libx264'
    )

    # remove video and audio file
    remove(f"{outputDir}/{videoFileNm}")
    remove(f"{outputDir}/{audioFileNm}")

    # rename the output file
    self.renameFile(outputDir, f'{fileNm}_merge.mp4', f'{title}.mp4')
    
    return
  
  # rename file with escape special character
  def renameFile(self, dirPath, oldName, newName):
    ESCAPE_CHAR = {'"', '*', ':', '<', '>', '?', '|'}
    
    escaped_newName = ''
    for c in newName:
      escaped_newName += '' if c in ESCAPE_CHAR else c

    rename(f'{dirPath}/{oldName}', f'{dirPath}/{escaped_newName}')

if __name__ == "__main__":
  lazyYtDownload().run()