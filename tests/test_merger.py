from unittest.mock import patch, Mock
from pytest import raises as pytest_raises

from os.path import exists
from pymediainfo import MediaInfo
from ffmpeg import Error as ffmpegError

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.service.merger import mergeVAS

@patch('src.service.merger.ffmpeg.run')
def test_mergeVAS_merge_fail(run_mock):
  run_mock.side_effect = Mock(ffmpegError('','',''))

  with pytest_raises(Exception):
    mergeVAS(
      outputPath=f'{OUTPUT_FOLDER_PATH}/test_video_out.mp4',
      videoPath='tests/testFiles/test_merger/test_video.mp4',
      audioPath='tests/testFiles/test_merger/test_audio.m4a',
      subtitlePath='tests/testFiles/test_merger/test_video.mp4',
      quiet=True
    )

def test_mergeVAS_no_video_n_audio():
  """
    Test if the function can raise exception if video and audio are not provided
  """
  with pytest_raises(Exception):
    mergeVAS(outputPath='', subtitlePath='', quiet=True)

def test_mergeVAS():
  """
    Perform a real merging with mergeVas
  """
  def get_track(mediaInfo : MediaInfo, trackType : str):
    for track in mediaInfo.tracks:
      if track.track_type == trackType:
        return track
    return None

  INPUT_FOLDER = 'tests/testFiles/test_merger'
  OUTPUT_FOLDER = f'{OUTPUT_FOLDER_PATH}'

  INPUT_VIDEO_PATH = f'{INPUT_FOLDER}/test_video.mp4'
  INPUT_AUDIO_PATH = f'{INPUT_FOLDER}/test_audio.m4a'
  OUTPUT_VIDEO_PATH = f'{OUTPUT_FOLDER}/test_video_out.mp4'

  prepare_output_folder()

  mergeVAS(
    outputPath=OUTPUT_VIDEO_PATH,
    videoPath=INPUT_VIDEO_PATH,
    audioPath=INPUT_AUDIO_PATH,
    subtitlePath=INPUT_VIDEO_PATH,
    quiet=True
  )

  # check if output file exists
  assert exists(OUTPUT_VIDEO_PATH)

  mediaInfo = MediaInfo.parse(OUTPUT_VIDEO_PATH)

  # check if the format of video track correct
  videoTrack = get_track(mediaInfo, 'Video')
  assert videoTrack is not None
  assert videoTrack.format == 'AVC'

  # check if the format of audio track correct
  audioTrack = get_track(mediaInfo, 'Audio')
  assert audioTrack is not None
  assert audioTrack.format == 'AAC'

  # check if the subtitle track exists
  subtitleTrack = get_track(mediaInfo, 'Text')
  assert subtitleTrack is not None