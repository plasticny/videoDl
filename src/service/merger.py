from enum import Enum

import ffmpeg

class Message (Enum):
  NO_INPUT_FILE = 'Must provide video or audio file path'
  MERGE_FAILED = 'Merge failed'

def mergeVAS (
    outputPath:str,
    videoPath:str=None, audioPath:str=None, subtitlePath:str=None,
    quiet=False
  ):
  """
    Merge video, audio and subtitle into one file. For lyd.

    Args:
      the corresponding components (video, audio, subtitle) will be extracted
      from the file in `videoPath`, `audioPath` and `subtitlePath`\n

      `videoPath` and `audioPath` can be None, but not both
  """
  if videoPath is None and audioPath is None:
    raise Exception(Message.NO_INPUT_FILE.value)

  # construct input streams and filename
  stream_n_nm = []
  if videoPath is not None:
    stream_n_nm.append(ffmpeg.input(videoPath)['v'])
  if audioPath is not None:
    stream_n_nm.append(ffmpeg.input(audioPath)['a'])
  if subtitlePath is not None:
    stream_n_nm.append(ffmpeg.input(subtitlePath)['s'])
  stream_n_nm.append(outputPath)

  # run ffmpeg
  ff : ffmpeg = ffmpeg.output(
    *stream_n_nm,
    vcodec='libx264', 
    acodec='aac', 
    scodec='mov_text',
    loglevel='quiet' if quiet else 'info'
  )
  
  try:
    ff.run(cmd='ffmpeg\\ffmpeg', overwrite_output=True, capture_stderr=True)
  except ffmpeg.Error:
    raise Exception(Message.MERGE_FAILED.value)