from __future__ import annotations
from uuid import uuid4
from os import listdir
from shutil import move as move_file
from typing import Union, Optional, Any

from src.section.Section import Section

from src.service.fileHelper import TEMP_FOLDER_PATH
from src.service.ffmpeg_helper import ff_in, run_ffmpeg, get_audio_sample_rate # type: ignore
from src.service.ytdlp import Ytdlp

from src.structs.option import Opt, TOpt
from src.structs.video_info import Subtitle, BundledFormat, MediaType


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
  sorting: Optional[str]

class BundledTDownloadOpt ():
  def __init__(self, video:TDownloadOpt, audio:TDownloadOpt):
    self.video = video
    self.audio = audio
# ============== typing ============== #


# ============== option ============== #
class DownloadOpt (Opt):
  @staticmethod
  def to_ytdlp_opt (obj: Opt):
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
          'sorting': obj.sorting
        },
        audio={
          **DownloadOpt.to_ytdlp_base_opt(obj),
          'format': obj.format.audio,
          'sorting': obj.sorting
        }
      )
    else:
      return {
        **DownloadOpt.to_ytdlp_base_opt(obj),
        'format': obj.format,
        'sorting': obj.sorting
      }

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

  def __init__(self, other: Optional[Opt] = None):
    super().__init__(other)
    
    # output
    self.output_nm: Optional[str] = None
    self.output_dir: Optional[str] = None
    # media
    self.media: Optional[MediaType] = None
    # format
    # if it is a string, only download the requested format
    # if it is a BundledFormat, download the video and audio, and merge them (deprecated)
    self.format: Optional[Union[str, BundledFormat]] = None
    # sorting format
    self.sorting: Optional[str] = None
    # subtitle
    # this section will write the subtitle if `subtitle` is not None
    self.subtitle: Optional[Subtitle] = None
    self.embed_sub: bool = False
    self.burn_sub: bool = False

  # === some setter functions === #
  def set_media (self, val: MediaType):
    self.media = val
  def set_format (self, val: str | BundledFormat):
    self.format = val
  def set_sorting (self, val: str):
    self.sorting = val
  def set_subtitle (self, sub: Optional[Subtitle], do_embed : bool, do_burn : bool):
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
  def run (self, opts: DownloadOpt, retry: int=0): # type: ignore
    assert isinstance(opts, DownloadOpt)
    opts = opts.copy()
    return super().run(self.__main, opts=opts, retry=retry)
        
  def __main (self, opts : DownloadOpt, retry:int) -> None:
    if opts.media == 'Video':
      self._download_video(opts, retry)
    elif opts.media == 'Audio':
      self._download_audio(opts, retry)
    else:
      raise Exception('Invalid media type')

  def _download_video (self, opts:DownloadOpt, retry:int) -> None:
    """ Handle download when the media is video """
    dl_opts = DownloadOpt.to_ytdlp_dl_opt(opts)
    sub_opts = DownloadOpt.to_ytdlp_sub_opt(opts)
    
    is_bundle = isinstance(dl_opts, BundledTDownloadOpt)
    has_sub = len(sub_opts['subtitleslangs']) > 0
    
    assert opts.url is not None
    if is_bundle:
      video_name = self._download_item(opts.url, dl_opts.video, retry)
      audio_name = self._download_item(opts.url, dl_opts.audio, retry)
    else:
      video_name = self._download_item(opts.url, dl_opts, retry)
      audio_name = video_name

    subtitle_name = self._download_item(opts.url, sub_opts, retry) if has_sub else None
  
    # merge if needed (bundle format or has subtitle)
    if is_bundle or has_sub:
      # get file paths
      video_path = f'{TEMP_FOLDER_PATH}/{video_name}'
      audio_path = f'{TEMP_FOLDER_PATH}/{audio_name}'
      subtitle_path = f'{TEMP_FOLDER_PATH}/{subtitle_name}' if has_sub else None

      temp_name = self._merge(
        video_path=video_path, audio_path=audio_path, subtitle_path=subtitle_path,
        do_embed_sub=opts.embed_sub, do_burn_sub=opts.burn_sub
      )
    else:
      temp_name = video_name
      
    # rename and move to the output dir
    assert opts.output_dir is not None
    out_nm = f'{opts.output_nm}.mp4'
    self._move_temp_file(temp_name, out_dir=opts.output_dir, out_nm=out_nm)
  
  def _download_audio (self, opts: DownloadOpt, retry: int):
    """ Handle download when the media is audio"""
    assert opts.url is not None

    dl_opts = DownloadOpt.to_ytdlp_dl_opt(opts)
    assert not isinstance(dl_opts, BundledTDownloadOpt)
    
    item_nm : str = self._download_item(opts.url, dl_opts, retry)
    item_path : str = f'{TEMP_FOLDER_PATH}/{item_nm}'

    sample_rate = get_audio_sample_rate(item_path)
    if sample_rate is None:
      raise Exception('No audio stream found')
    
    # convert the download item to flac
    temp_nm = f'{uuid4().__str__()}.flac'
    streams_n_output: list[Union[object, str]] = [
      ff_in(item_path)['a'],
      f'{TEMP_FOLDER_PATH}/{temp_nm}'
    ]
    kwargs: dict[str, Union[str, int]] = {
      'acodec': 'flac',
      'ar': sample_rate,
      'loglevel': 'quiet'
    }
    run_ffmpeg(streams_n_output, kwargs)
  
    # move the temp file to the output directory
    assert opts.output_dir is not None
    self._move_temp_file(temp_nm, out_dir=opts.output_dir, out_nm=f'{opts.output_nm}.flac')

  def _download_item (self, url: str, opts: Union[TDownloadOpt, TDlSubtitleOpt], retry: int) -> str:  
    """ Return: the name of the downloaded file """
    tryCnt = 0
    while True:
      try:
        Ytdlp(opts).download(url)
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
    raise Exception('Download failed, file not found')
  
  def _merge (
      self,
      video_path:str, audio_path:str, subtitle_path: Optional[str],
      do_embed_sub:bool=False, do_burn_sub:bool=False,
      quiet:bool=False
    ):
    """
      Merge video, audio and subtitles\n      
      Return the name of the merged file
    """
    MERGE_NM = f'{uuid4().__str__()}.mp4'
        
    streams_n_output: list[Any] = [ff_in(video_path)['v'], ff_in(audio_path)['a']]
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
        kwargs['vf'] = f"subtitles='{sub_path}':'force_style=Fontsize=12\,MarginV=3'" # type: ignore
        # when use filter, vcodec and acodec must be specified
        kwargs['vcodec'] = 'libx264'
        kwargs['acodec'] = 'aac'

    run_ffmpeg(streams_n_output, kwargs)
    
    return MERGE_NM
  
  def _move_temp_file (self, temp_nm: str, out_dir: str, out_nm: str):
    """ rename temp file and move it to output directory """
    assert out_nm is not None
    
    # escape special characters in the output name
    ESCAPE_CHAR = {'"', '*', ':', '<', '>', '?', '|', '/', '\r'}
    output_nm = ''
    for c in out_nm:
      output_nm += '' if c in ESCAPE_CHAR else c
    if len(output_nm) > 100:
      output_nm = output_nm[:100] + '.mp4'
    
    move_file(f'{TEMP_FOLDER_PATH}/{temp_nm}', f'{out_dir}/{output_nm}')
    self.logger.info(f'Temp file is moved from {TEMP_FOLDER_PATH}/{temp_nm} to {out_dir}/{output_nm}')
