import service.packageChecker as packageChecker
packageChecker.check()

from service.urlHelper import getSource, UrlSource
from service.MetaData import MetaData, VideoMetaData
from service.YtDlpHelper import Opts
from service.fileHelper import perpare_temp_folder, clear_temp_folder, TEMP_FOLDER_PATH

from os import rename, remove, listdir
from os.path import exists
from uuid import uuid4
from enum import Enum
import ffmpeg

from section.Section import Section, HeaderType
from section.UrlSection import UrlSection
from section.DownloadSection import DownloadSection
from section.LoginSection import LoginSection
from section.SubTitleSection import SubTitleSection
from section.OutputSection import OutputSection

class Message (Enum):
  MERGE_FAILED = 'Merge failed'

class lazyYtDownload:
  def run (self, loop=True):
    print("----------------- Downlaod -----------------", end='\n\n')

    perpare_temp_folder()

    while True:
      opts = Opts()

      url = UrlSection(title='Url').run()

      opts = self.configDownload(url, opts)

      # check the number of video need to download
      md = MetaData.fetchMetaData(url)
      videos : list[VideoMetaData] = []
      if md.isPlaylist():
        videos.extend(md.videos)
      else:
        videos.append(md)

      # download
      for idx, v in enumerate(videos):
        try:
          Section(title=f'Video {idx+1} of {len(videos)}').run(
            self.download, opts=opts,
            title=v.title, url=v.url
          )
        finally:
          clear_temp_folder()

      if not loop:
        break
    return

  def configDownload(self, url, opts) -> Opts:
    # ask login    
    opts = self.login(url, opts=opts)

    # set up download
    # subtitle, output dir
    opts = Section(title='Set up download').run(self.setup, url=url, opts=opts)

    return opts
  
  def login(self, url:str, opts:Opts) -> Opts:
    # ask login if bilibili
    if getSource(url) == UrlSource.BILIBILI:
      return LoginSection(title='Login').run(opts)
    return opts

  def setup(self, url, opts) -> Opts:
    # subtitle
    opts = SubTitleSection(
      title='Subtitle',
      headerType=HeaderType.SUB_HEADER
    ).run(url, opts)

    # output dir
    opts = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts, askName=False)

    return opts

  def download(self, opts:Opts, title, url):
    """
      Download video, audio and subtitles separately, then merge them.

      Args hint:
        `title` will be the title of the output video
    """

    # set a random output name
    fileNm = uuid4().__str__()
    # store the output dir path and replace it with temp folder
    outputDir = opts.outputDir
    opts = opts.copy()
    opts.outputDir = TEMP_FOLDER_PATH
    opts.outputName = fileNm

    # download subtitle
    subtitleFileNm = None
    if opts.writeSubtitles or opts.writeAutomaticSub:
      s_opts = opts.copy()
      s_opts.skip_download = True # skip download doesnt skip subtitle

      DownloadSection(
        title="Downloading subtitle",
        headerType=HeaderType.SUB_HEADER
      ).run(url, s_opts, retry=2)

      subtitleFileNm = listdir(TEMP_FOLDER_PATH)[0]

      opts.writeSubtitles = False
      opts.writeAutomaticSub = False

    # download video
    opts.format = "bv*[ext=mp4]"
    opts.outputName = fileNm+'.mp4'
    DownloadSection(
      title="Downloading video",
      headerType=HeaderType.SUB_HEADER
    ).run(url, opts, retry=2)

    # download audio
    opts.format = "ba*[ext=m4a]"
    opts.outputName = fileNm+'.m4a'
    DownloadSection(
      title="Downloading audio",
      headerType=HeaderType.SUB_HEADER
    ).run(url, opts, retry=2)

    # merge
    videoFileNm = f'{fileNm}.mp4'
    audioFileNm = f'{fileNm}.m4a'
    mergeFileNm = f'{fileNm}_merge.mp4'
    Section(title="Merging").run(
      bodyFunc=self.merge,
      # output paths
      outputPath=f"{TEMP_FOLDER_PATH}/{mergeFileNm}",
      # input paths
      videoPath=f"{TEMP_FOLDER_PATH}/{videoFileNm}", 
      audioPath=f"{TEMP_FOLDER_PATH}/{audioFileNm}",
      subtitlePath=f"{TEMP_FOLDER_PATH}/{subtitleFileNm}" if subtitleFileNm is not None else None,
      # ffmpeg location
      ffmpegLoaction=opts.ffmpeg_location,
      # subtitle options
      embedSubtitle=opts.embedSubtitle,
      burnSubtitle=opts.burnSubtitle
    )

    # rename the output file
    self.renameFile(
      mergeFileNm, f'{title}.mp4',
      dirPath=TEMP_FOLDER_PATH, toDirPath=outputDir,
      overwrite=True
    )
        
    return
  
  def merge(
      self, outputPath:str,
      videoPath:str, audioPath:str, subtitlePath:str,
      ffmpegLoaction:str, 
      embedSubtitle:bool=False, burnSubtitle:bool=False,
      quiet:bool=False
    ):
    """Merge video, audio and subtitles"""
    # stream and output
    streams_n_output = []
    streams_n_output.append(ffmpeg.input(videoPath)['v'])
    streams_n_output.append(ffmpeg.input(audioPath)['a'])
    if subtitlePath is not None and embedSubtitle:
      streams_n_output.append(ffmpeg.input(subtitlePath)['s'])
    streams_n_output.append(outputPath)

    # kwargs
    kwargs = {
      # basic merge settings
      'vcodec': 'libx264', 'acodec': 'aac',
      'loglevel': 'quiet' if quiet else 'info',
    }
    # embed subtitle
    if subtitlePath is not None and embedSubtitle:
      kwargs['scodec'] = 'mov_text'
    # burn subtitle
    if subtitlePath is not None and burnSubtitle: 
      kwargs['vf'] = f"subtitles='{subtitlePath}':'force_style=Fontsize=12\,MarginV=3'"

    try:
      ff : ffmpeg = ffmpeg.output(*streams_n_output,**kwargs)
      ff.run(cmd=f'{ffmpegLoaction}\\ffmpeg')
    except ffmpeg.Error:
      raise Exception(Message.MERGE_FAILED.value)

    return
  
  def renameFile(self, oldName, newName, dirPath, toDirPath=None, overwrite=False):
    """
      Rename file with escape special character

      Args hint:
        `dirPath` is the directory of the file.\n
        If `toDirPath` is provided, the file will also move to the given dir\n
        If `overwrite` is True, the file will overwrite the file with the same name in the target dir
    """
    ESCAPE_CHAR = {'"', '*', ':', '<', '>', '?', '|'}
    
    escaped_newName = ''
    for c in newName:
      escaped_newName += '' if c in ESCAPE_CHAR else c
    target_name = f'{dirPath if toDirPath is None else toDirPath}/{escaped_newName}'

    if overwrite and exists(target_name):
      remove(target_name)
    rename(f'{dirPath}/{oldName}',target_name)

if __name__ == "__main__":
  lazyYtDownload().run()