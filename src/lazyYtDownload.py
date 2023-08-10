from dlConfig import dlConfig

from service.merger import merge
from service.YtFetcher import getYtSongTitle
from os import remove, rename
from uuid import uuid4

from section.UrlSection import UrlSection
from section.DownloadSection import DownloadSection
from section.SetUpDownloadSection import SetUpDownloadSection

def run ():
  print("----------------- Downlaod -----------------", end='\n\n')

  while True:
    config = dlConfig()

    # ask the url
    config.url = UrlSection(title='Url').run()
    
    # ask the output dir
    setupConfig = SetUpDownloadSection(
      title='Set up download', config=config,
      subtitle=False, format=False, outputName=False, h264=False
    ).run()
    config.overwriteConfigBy(setupConfig)

    config.outputName = uuid4()

    # download video
    config.outputFormat = '"bv*[ext=mp4]"'
    DownloadSection(title="Downloading", config=config).run()

    # download audio
    config.outputFormat = '"ba*[ext=m4a]"'
    DownloadSection(title="Downloading", config=config).run()

    # merge
    filePath = f'{config.outputDir}/{config.outputName}'
    videoFilePath = f'{filePath}.mp4'
    audioFilePath = f'{filePath}.m4a'
    mergeFilePath = f'{filePath}_merge.mp4'
    merge(
      video = videoFilePath,
      audio = audioFilePath,
      outputDir = mergeFilePath
    )

    # remove video and audio file
    remove(videoFilePath)
    remove(audioFilePath)

    # rename the output file
    title = getYtSongTitle(config.url)
    ESCAPE_CHR = ['"', '*', '/', ':', '<', '>', '?', '\\', '|', ' ', '&']
    for chr in ESCAPE_CHR:
      title = title.replace(chr, '_')
    rename(mergeFilePath, f'{config.outputDir}/{title}.mp4')