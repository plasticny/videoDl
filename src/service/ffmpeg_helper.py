from ffmpeg import input as _input, output as ff_out, Error as _Error
from os import devnull
from os.path import isfile
from subprocess import check_call, Popen, PIPE
from typing import Union, Iterator

from src.service.fileHelper import FFMPEG_FOLDER_PATH
from src.service.logger import Logger
from src.structs.video_info import Stream

# export some functions of ffmpeg module
ff_in = _input
ff_Error = _Error

LOGGER = Logger()

def run_ffmpeg (stream_n_output : list, kwargs : dict):
  """ Run ffmpeg with the specified streams and options """
  FFMPEG_PATH = f'{FFMPEG_FOLDER_PATH}\\ffmpeg'

  LOGGER.debug(f'Running ffmpeg with streams: {stream_n_output}')
  LOGGER.debug(f'Running ffmpeg with ffmpeg options: {kwargs}')
  LOGGER.debug(f'Running ffmpeg with ffmpeg path: {FFMPEG_PATH}')

  try:
    ff_out(*stream_n_output, **kwargs).run(cmd=FFMPEG_PATH)
  except ff_Error:
    raise Exception('ffmpeg failed')

def get_streams (file_path : str) -> list[Stream]:
  """ get streams from the file"""
  """ re-implementing FFProbe of ffprobe-python module """
  FFPROBE_PATH = f'{FFMPEG_FOLDER_PATH}\\ffprobe'

  try:
    with open(devnull, 'w') as tempf:
      check_call([FFPROBE_PATH, '-h'], stdout=tempf, stderr=tempf)
  except FileNotFoundError:
    raise IOError('ffprobe not found.')
  
  if not isfile(file_path):
    raise IOError('No such media file ' + file_path)
  
  p = Popen([FFPROBE_PATH, '-show_streams', file_path], stdout=PIPE, stderr=PIPE, shell=True)  
  iterator_ls : list[Iterator] = [
    iter(p.stdout.readline, b''),
    iter(p.stderr.readline, b'')
  ]
  
  streams : list[Stream] = []
  data_lines : list[bytes] = []
  is_stream = False
  
  for it in iterator_ls:
    for line in it:
      line = line.decode('UTF-8')
      
      if '[STREAM]' in line:
        is_stream = True
        data_lines = []
      elif '[/STREAM]' in line and is_stream:
        is_stream = False
        streams.append(Stream(data_lines))
      elif is_stream:
        data_lines.append(line)
      
  return streams

def get_audio_sample_rate (file_path : str) -> Union[int, None]:
  """ Get the sample rate of the audio file """
  """ If the file has no audio stream, return None"""
  for stream in get_streams(file_path):
    if not stream.is_audio:
      continue
    return stream.sample_rate
  return None
