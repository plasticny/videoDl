from enum import Enum

import ffmpeg
from pymediainfo import MediaInfo, Track

class Message (Enum):
  NO_INPUT_TRACK = 'No video or audio track found'
  MERGE_FAILED = 'Merge failed'

def checkTrack(filePath:str, trackType:str) -> bool:
  """check if the file has the track type"""
  if filePath is None:
    return False
  for track in MediaInfo.parse(filePath).tracks:
    if track.track_type == trackType:
      return True
  return False

def mergeVAS (
    outputPath:str,
    videoPath:str=None, audioPath:str=None, subtitlePath:str=None,
    ffmpegLocation:str='ffmpeg',
    quiet=False
  ):
  """
    Merge video, audio and subtitle into one file. For lyd.

    Args:
      the corresponding components (video, audio, subtitle) will be extracted
      from the file in `videoPath`, `audioPath` and `subtitlePath`\n

      `videoPath` and `audioPath` can be None, but not both\n

      `ffmpegLocation` is the dir of ffmpeg.exe. 
      For example, it should be `ffmpeg` if the .exe is stored in sub folder `ffmpeg`\n
  """
  # get input tracks
  videoTrack : ffmpeg = ffmpeg.input(videoPath)['v'] if checkTrack(videoPath, 'Video') else None
  audioTrack : ffmpeg = ffmpeg.input(audioPath)['a'] if checkTrack(audioPath, 'Audio') else None
  subtitleTrack : ffmpeg = ffmpeg.input(subtitlePath)['s'] if checkTrack(subtitlePath, 'Text') else None

  # check video track and audio track exist
  if videoTrack is None and audioTrack is None:
    raise Exception(Message.NO_INPUT_TRACK.value)

  # construct input streams and filename
  stream_n_nm = []
  if videoTrack is not None:
    stream_n_nm.append(videoTrack)
  if audioTrack is not None:
    stream_n_nm.append(audioTrack)
  if subtitleTrack is not None:
    stream_n_nm.append(subtitleTrack)
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
    ff.run(cmd=f'{ffmpegLocation}\\ffmpeg')
  except ffmpeg.Error:
    raise Exception(Message.MERGE_FAILED.value)