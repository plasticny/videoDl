import service.packageChecker as packageChecker
packageChecker.check()

from service.urlHelper import getSource, UrlSource
from service.MetaData import MetaData, VideoMetaData, fetchMetaData
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
      url = UrlSection(title='Url').run()
      # ask login    
      temp_opts : Opts = self.login(url, opts=Opts())

      # fetch metadata
      print('Getting download information...\n')
      md = fetchMetaData(url, temp_opts)

      # get video metadata list
      videos_md : list[VideoMetaData] = md.videos if md.isPlaylist() else [md]
      # prepare opts list
      opts_ls : list[Opts] = [temp_opts.copy() for _ in range(len(videos_md))]

      # set up download
      # subtitle, output dir
      opts_ls:list[Opts] = Section(title='Set up download').run(self.setup, md=md, opts_ls=opts_ls)

      # download
      assert len(videos_md) == len(opts_ls)
      for idx, (md, opts) in enumerate(zip(videos_md, opts_ls)):
        try:
          Section(title=f'Video {idx+1} of {len(videos_md)}').run(
            self.download, opts=opts, md=md
          )
        finally:
          clear_temp_folder()

      if not loop:
        break
    return
  
  def login(self, url:str, opts:Opts) -> Opts:
    # ask login if bilibili
    if getSource(url) == UrlSource.BILIBILI:
      return LoginSection(title='Login').run(opts)
    return opts

  def setup(self, md:MetaData, opts_ls:list[Opts]) -> list[Opts]:
    # subtitle
    opts_ls = SubTitleSection(
      title='Subtitle',
      headerType=HeaderType.SUB_HEADER
    ).run(md, opts_ls)

    # output dir
    opts_ls = OutputSection(
      title='Output',
      doShowFooter=False,
      headerType=HeaderType.SUB_HEADER
    ).run(opts_ls, askName=False)

    return opts_ls

  def download(self, opts:Opts, md:VideoMetaData):
    """
      Download video, audio and subtitles separately, then merge them.

      Args hint:
        `title` will be the title of the output video
    """

    # set a random output name
    temp_nm = uuid4().__str__()
    # store the output dir path
    outputDir = opts.outputDir
    
    opts = opts.copy()
    # use temp folder and temp name
    opts.outputDir = TEMP_FOLDER_PATH
    opts.outputName = temp_nm

    # download subtitle
    subtitleFileNm = None
    if opts.writeSubtitles or opts.writeAutomaticSub:        
      s_opts = opts.copy()
      s_opts.skip_download = True # skip download doesnt skip subtitle

      DownloadSection(
        title="Downloading subtitle",
        headerType=HeaderType.SUB_HEADER
      # ).run(url, s_opts, retry=2, info_path='C:\\Users\\22203\\Documents\\desktop\\script\\videoDl\\src\\test.json')
      ).run(md.url, s_opts, retry=2)

      assert len(listdir(TEMP_FOLDER_PATH)) == 1
      subtitleFileNm = listdir(TEMP_FOLDER_PATH)[0]

      # not download subtitle anymore
      opts.removeSubtitle()

    print(md.audio_formats)
    if 'm4a' in md.audio_formats:
      self.download_separatly(opts, md, temp_nm, outputDir, subtitleFileNm)
    else:
      self.download_mp4(opts, md, temp_nm, outputDir)
        
    return
  
  def download_separatly(
      self, opts:Opts, md:VideoMetaData,
      temp_nm:str, outputDir:str, subtitleFileNm:str
    ):
    """Download video and audio separately, then merge video, audio & subtitle. For better quality"""
    # video
    opts.format = "bv*[ext=mp4]"
    opts.outputName = temp_nm+'.mp4'
    DownloadSection(
      title="Downloading video",
      headerType=HeaderType.SUB_HEADER
    ).run(md.url, opts, retry=2)

    # audio
    opts.format = "ba*[ext=m4a]"
    opts.outputName = temp_nm+'.m4a'
    DownloadSection(
      title="Downloading audio",
      headerType=HeaderType.SUB_HEADER
    ).run(md.url, opts, retry=2)

    # merge
    videoFileNm = f'{temp_nm}.mp4'
    audioFileNm = f'{temp_nm}.m4a'
    mergeFileNm = f'{temp_nm}_merge.mp4'
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
      mergeFileNm, f'{md.title}.mp4',
      dirPath=TEMP_FOLDER_PATH, toDirPath=outputDir,
      overwrite=True
    )
  
  def download_mp4(
    self, opts:Opts, md:VideoMetaData,
    temp_nm:str, outputDir:str
  ):
    """Let yt-dlp download a mp4 file directly"""
    # not specify download format
    outputName = temp_nm+'.mp4'
    
    opts.format = None
    opts.outputName = outputName
    DownloadSection(
      title="Downloading",
      headerType=HeaderType.SUB_HEADER
    ).run(md.url, opts, retry=2)
    
    self.renameFile(
      outputName, f'{md.title}.mp4',
      dirPath=TEMP_FOLDER_PATH, toDirPath=outputDir,
      overwrite=True
    )
  
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
    streams_n_output.append(ffmpeg.input(videoPath, hwaccel='auto')['v'])
    streams_n_output.append(ffmpeg.input(audioPath)['a'])
    if subtitlePath is not None and embedSubtitle:
      streams_n_output.append(ffmpeg.input(subtitlePath)['s'])
    streams_n_output.append(outputPath)

    # kwargs
    kwargs = {
      # basic merge settings
      'vcodec': 'libx264', 'acodec': 'aac',
      # 'vcodec': 'h264_nvenc', 'acodec': 'aac',
      # 'vcodec': 'hevc_nvenc', 'acodec': 'aac',
      'fps_mode': 'passthrough',
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
    ESCAPE_CHAR = {'"', '*', ':', '<', '>', '?', '|', '/'}
    
    escaped_newName = ''
    for c in newName:
      escaped_newName += '' if c in ESCAPE_CHAR else c
    target_name = f'{dirPath if toDirPath is None else toDirPath}/{escaped_newName}'

    if overwrite and exists(target_name):
      remove(target_name)
    rename(f'{dirPath}/{oldName}',target_name)

if __name__ == "__main__":
  lazyYtDownload().run()