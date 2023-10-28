from dlConfig import dlConfig, DefaultConfig

from service.merger import merge
from service.YtFetcher import getYtSongTitle
from service.urlHelper import getSource, UrlSource

from os import remove, rename
from os.path import exists
from uuid import uuid4

from section.UrlSection import UrlSection
from section.DownloadSection import DownloadSection
from section.SetUpDownloadSection import SetUpDownloadSection
from section.ListSubtitleSection import ListSubtitleSection
from section.LoginSection import LoginSection

def login(config : dlConfig) -> str:
  # ask login if bilibili
  if getSource(config.url) == UrlSource.BILIBILI:
    return LoginSection(title='Login').run()
  else:
    return DefaultConfig.cookieFile.value

def configDownload() -> dlConfig:
  config = dlConfig()

  # ask the urls
  config.url = UrlSection(title='Url').run()

  # ask login    
  config.cookieFile = login(config)

  # list subtitle
  ListSubtitleSection(title='List Subtitle', config=config).run()

  # ask the output dir
  setupConfig = SetUpDownloadSection(
    title='Set up download', config=config,
    format=False, outputName=False
  ).run()
  config.overwriteConfigBy(setupConfig)

  # set a random output name
  config.outputName = uuid4()

  return config

def run (loop=True):
  print("----------------- Downlaod -----------------", end='\n\n')

  while True:
    config = configDownload()

    # download section, 2 retry when download failed
    download_section = DownloadSection(title="Downloading", config=config, retry=2)

    filePath = f'{config.outputDir}/{config.outputName}'

    # download video
    videoFilePath = f'{filePath}.mp4'
    config.outputFormat = '"bv*[ext=mp4]"'
    download_section.run()

    # download audio
    audioFilePath = f'{filePath}.m4a'
    config.outputFormat = '"ba*[ext=m4a]"'
    download_section.run()

    # merge
    mergeFilePath = f'{filePath}_merge.mp4'
    merge(
      videoPath = videoFilePath,
      audioPath = audioFilePath,
      outputDir = mergeFilePath,
      videoFormat= 'libx264'
    )

    # remove video and audio file
    remove(videoFilePath)
    remove(audioFilePath)

    # rename the output file
    title = getYtSongTitle(config.url, escape=True)
    rename(mergeFilePath, f'{config.outputDir}/{title}.mp4')

    if not loop:
      break

if __name__ == "__main__":
  run()