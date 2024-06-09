from __future__ import annotations
from yt_dlp import YoutubeDL
from uuid import uuid4
from ffmpeg import input as ff_in, output as ff_out, Error as ff_Error
from os import listdir
from shutil import move as move_file
from typing import Literal

from src.section.Section import Section

from src.service.fileHelper import TEMP_FOLDER_PATH, FFMPEG_FOLDER_PATH

from src.structs.option import IOpt, TOpt
from src.structs.video_info import Subtitle, BundledFormat


# ============== typing ============== #  
class TDownloadOptBase (TOpt):
  """ base options for downloading item """
  # output
  outtmpl: str
  paths : dict[str, str]
  # others
  overwrites: bool
  
class TDlSubtitleOpt (TDownloadOptBase):
  """ additional options for downloading subtitle """
  writeautomaticsub: bool
  writesubtitles: bool
  subtitleslangs: list[str]
  skip_download: bool

class TDownloadOpt (TDownloadOptBase):
  """ additional options for downloading video or audio """
  format: str

class BundledTDownloadOpt ():
  def __init__(self, video:TDownloadOpt, audio:TDownloadOpt):
    self.video = video
    self.audio = audio
# ============== typing ============== #


# ============== option ============== #
class DownloadOpt (IOpt):
  @staticmethod
  def to_ytdlp_opt():
    """
      DONT USE THIS\n
      Use DownloadOpt.to_ytdlp_dl_opts or DownloadOpt.to_ytdlp_sub_opts instead
    """
    assert False, 'Use DownloadOpt.to_ytdlp_dl_opts or DownloadOpt.to_ytdlp_sub_opts instead'
 
  @staticmethod
  def to_ytdlp_base_opt (obj : DownloadOpt) -> TDownloadOptBase:
    assert obj.output_dir is not None
    return {
      **super(DownloadOpt, obj).to_ytdlp_opt(obj),
      # use a temp name first
      'outtmpl': f'{uuid4().__str__()}.%(ext)s',
      # download to temp folder first
      'paths': { 'home': TEMP_FOLDER_PATH },
      'overwrites': True
    }
 
  @staticmethod
  def to_ytdlp_dl_opt(obj : DownloadOpt) -> TDownloadOpt | BundledTDownloadOpt:
    """ Convert DownloadOpt to YoutubeDL options for downloading video or audio """
    assert isinstance(obj.format, str) or isinstance(obj.format, BundledFormat)
    
    if isinstance(obj.format, BundledFormat):      
      return BundledTDownloadOpt(
        video={
          **DownloadOpt.to_ytdlp_base_opt(obj),
          'format': obj.format.video,
        },
        audio={
          **DownloadOpt.to_ytdlp_base_opt(obj),
          'format': obj.format.audio,
        }
      )
    else:
      res : TDownloadOpt = {
        **DownloadOpt.to_ytdlp_base_opt(obj),
        'format': obj.format
      }
      return res

  @staticmethod
  def to_ytdlp_sub_opt(obj : DownloadOpt) -> TDlSubtitleOpt:
    """ Convert DownloadOpt to YoutubeDL options for downloading subtitle """
    base_opt = DownloadOpt.to_ytdlp_base_opt(obj)
    if obj.subtitle is None:
      return {
        **base_opt,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'subtitleslangs': [],
        # skip_download = True means skip downloading the video
        # it still download the subtitle
        'skip_download': True
      }
    else:
      return {
        **base_opt,
        'writesubtitles': not obj.subtitle.isAuto,
        'writeautomaticsub': obj.subtitle.isAuto,
        'subtitleslangs': [obj.subtitle.code],
        'skip_download': True
      }

  def __init__(self, iIOpt : IOpt = None):
    """
      Args:
        iIOpt: IOpt. If it is not None, copy the value from it
    """
    super().__init__()
    
    # copy from iIOpt
    if iIOpt is not None:
      assert isinstance(iIOpt, IOpt)
      self.url = iIOpt.url
      self.cookie_file_path = iIOpt.cookie_file_path
    
    # output
    self.output_nm : str = None
    self.output_dir : str = None
    # media
    self.media : Literal['Video', 'Audio'] = None
    # format
    # if it is a string, only download the requested format
    # if it is a BundledFormat, download the video and audio, and merge them
    self.format : str | BundledFormat = None
    # subtitle
    # this section will write the subtitle if `subtitle` is not None
    self.subtitle : Subtitle = None
    self.embed_sub : bool = False
    self.burn_sub : bool = False
  
  # === some setter functions === #
  def set_media (self, val : Literal['Video', 'Audio']):
    self.media = val
  def set_format (self, val : str | BundledFormat):
    self.format = val
  def set_subtitle (self, sub : Subtitle, do_embed : bool, do_burn : bool):
    self.subtitle = sub
    self.embed_sub = do_embed
    self.burn_sub = do_burn
  # === some setter functions === #  
# ============== option ============== #


class DownloadSection (Section) :
  """
    download a video
  
    Args:
      retry: int, the times of try to download again, default is 0
  """  
  def run(self, opts:DownloadOpt, retry:int=0):
    assert isinstance(opts, DownloadOpt)
    opts = opts.copy()
    return super().run(self.__main, opts=opts, retry=retry)
        
  def __main (self, opts : DownloadOpt, retry:int):
    URL = opts.url

    dl_opts = DownloadOpt.to_ytdlp_dl_opt(opts)
    sub_opts = DownloadOpt.to_ytdlp_sub_opt(opts)
    
    is_bundle = isinstance(dl_opts, BundledTDownloadOpt)
    has_sub = len(sub_opts['subtitleslangs']) > 0
    
    if is_bundle:
      video_name = self._download_item(URL, dl_opts.video, retry)
      audio_name = self._download_item(URL, dl_opts.audio, retry)
    else:
      video_name = self._download_item(URL, dl_opts, retry)
      audio_name = video_name

    if has_sub:
      subtitle_name = self._download_item(URL, sub_opts, retry)
    else:
      subtitle_name = None
      
    # merge if needed (bundle format or has subtitle)
    if is_bundle or has_sub:
      # get file paths
      video_path = f'{TEMP_FOLDER_PATH}/{video_name}'
      audio_path = f'{TEMP_FOLDER_PATH}/{audio_name}'

      if has_sub:
        subtitle_path = f'{TEMP_FOLDER_PATH}/{subtitle_name}'
      else:
        subtitle_path = None

      temp_name = self._merge(
        video_path=video_path, audio_path=audio_path, subtitle_path=subtitle_path,
        do_embed_sub=opts.embed_sub, do_burn_sub=opts.burn_sub
      )
    else:
      temp_name = video_name
      
    # rename and move to the output dir
    out_nm = f'{opts.output_nm}.mp4'
    self._move_temp_file(temp_name, out_dir=opts.output_dir, out_nm=out_nm)

  def _download_item (self, url:str, opts:TDownloadOpt | TDlSubtitleOpt, retry:int) -> str:  
    """ Return: the name of the downloaded file """
    tryCnt = 0
    while True:
      try:
        # NOTE: add .copy(), else the download function change the value of opts
        YoutubeDL(opts.copy()).download([url])
        # YoutubeDL(opts.copy()).download_with_info_file(info_filename=info_path)
        break
      except Exception as e:
        tryCnt += 1
        if tryCnt > retry:
          raise Exception('Download failed', e)
        print(f'Retry {tryCnt} times')
        
    # get the file full name (with extension)
    output_dir = opts['paths']['home']
    output_nm = opts['outtmpl'][:36] # len of uuid4 is 36
    for file_nm in listdir(output_dir):
      if file_nm.startswith(output_nm):
        return file_nm
    # the file should be found
    raise Exception('Download failed')
  
  def _merge (
      self,
      video_path:str, audio_path:str, subtitle_path:str,
      do_embed_sub:bool=False, do_burn_sub:bool=False,
      ffmpeg_location:str=FFMPEG_FOLDER_PATH, quiet:bool=False
    ):
    """
      Merge video, audio and subtitles\n      
      Return the name of the merged file
    """
    MERGE_NM = f'{uuid4().__str__()}.mp4'
        
    streams_n_output = []
    streams_n_output.append(ff_in(video_path)['v'])
    streams_n_output.append(ff_in(audio_path)['a'])
    if subtitle_path is not None and do_embed_sub:
      streams_n_output.append(ff_in(subtitle_path)['s'])
    streams_n_output.append(f'{TEMP_FOLDER_PATH}/{MERGE_NM}')

    # kwargs
    kwargs = {
      # 'vcodec': 'h264_nvenc', 'acodec': 'aac',
      # 'vcodec': 'hevc_nvenc', 'acodec': 'aac',
      # 'pix_fmt': 'p010le', # 10bit
      # 'preset': 'p7',
      # 'tune': 'hq',
      # 'level': '6.2',
      # 'profile': 'rext',
      # 'tier': 'high',
      'vcodec': 'copy', 'acodec': 'copy',
      'fps_mode': 'passthrough',
      'loglevel': 'quiet' if quiet else 'info',
    }
    if subtitle_path is not None:
      # embed subtitle
      if do_embed_sub:
        kwargs['scodec'] = 'mov_text'
      # burn subtitle
      if do_burn_sub:
        sub_path = subtitle_path.replace('\\', '/').replace(':', '\\:')
        kwargs['vf'] = f"subtitles='{sub_path}':'force_style=Fontsize=12\,MarginV=3'"
        # when use filter, vcodec and acodec must be specified
        kwargs['vcodec'] = 'libx264'
        kwargs['acodec'] = 'aac'

    try:
      ff_out(*streams_n_output,**kwargs).run(cmd=f'{ffmpeg_location}\\ffmpeg')
    except ff_Error:
      raise Exception('Merge failed')
    
    return MERGE_NM
  
  def _move_temp_file (self, temp_nm, out_dir, out_nm):
    """ rename temp file and move it to output directory """
    assert out_nm is not None
    
    # escape special characters in the output name
    ESCAPE_CHAR = {'"', '*', ':', '<', '>', '?', '|', '/'}
    output_nm = ''
    for c in out_nm:
      output_nm += '' if c in ESCAPE_CHAR else c
    
    move_file(f'{TEMP_FOLDER_PATH}/{temp_nm}', f'{out_dir}/{output_nm}')
    self.logger.info(f'Temp file is moved from {TEMP_FOLDER_PATH}/{temp_nm} to {out_dir}/{output_nm}')
