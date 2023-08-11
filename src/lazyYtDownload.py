from dlConfig import dlConfig

from service.merger import merge
from service.YtFetcher import getYtSongTitle
from os import remove, rename
from os.path import exists
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
    filePath = f'{config.outputDir}/{config.outputName}'
    videoFilePath = f'{filePath}.mp4'
    config.outputFormat = '"bv*[ext=mp4]"'
    while (not(exists(videoFilePath))):
      # try to download until success
      DownloadSection(title="Downloading", config=config).run()

    # download audio
    audioFilePath = f'{filePath}.m4a'
    config.outputFormat = '"ba*[ext=m4a]"'
    while (not(exists(audioFilePath))):
      # try to download until success
      DownloadSection(title="Downloading", config=config).run()

    # merge
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