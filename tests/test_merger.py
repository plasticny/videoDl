""" NOTE: vm on git action already install ffmpeg """

from unittest.mock import patch
from pytest import raises as pytest_raises

from os.path import exists
from pymediainfo import MediaInfo
from enum import Enum

from tests.testFileHelper import prepare_output_folder
from tests.fakers import fake_CompletedProcess

from src.service.merger import merge

class TrackType(Enum):
  VIDEO = 'Video'
  AUDIO = 'Audio'
  TEXT = 'Text'

def get_track(mediaInfo : MediaInfo, trackType : TrackType):
  for track in mediaInfo.tracks:
    if track.track_type == trackType.value:
      return track
  return None

def test_merge():
  INPUT_FOLDER = 'tests/testFiles/test_merger'
  OUTPUT_FOLDER = 'tests/testFiles/output'

  INPUT_VIDEO_PATH = f'{INPUT_FOLDER}/test_video.mp4'
  INPUT_AUDIO_PATH = f'{INPUT_FOLDER}/test_audio.m4a'
  OUTPUT_VIDEO_PATH = f'{OUTPUT_FOLDER}/test_video_out.mp4'

  prepare_output_folder()

  merge(
    videoPath=INPUT_VIDEO_PATH,
    audioPath=INPUT_AUDIO_PATH,
    outputDir=OUTPUT_VIDEO_PATH,
    quiet=True
  )

  # check if output file exists
  assert exists(OUTPUT_VIDEO_PATH)

  mediaInfo = MediaInfo.parse(OUTPUT_VIDEO_PATH)

  # check if the format of video track correct
  videoTrack = get_track(mediaInfo, TrackType.VIDEO)
  assert videoTrack is not None
  assert videoTrack.format == 'AVC'

  # check if the format of audio track correct
  audioTrack = get_track(mediaInfo, TrackType.AUDIO)
  assert audioTrack is not None
  assert audioTrack.format == 'AAC'

  # check if the subtitle track exists
  subtitleTrack = get_track(mediaInfo, TrackType.TEXT)
  assert subtitleTrack is not None

@patch('src.service.merger.runCommand')
def test_merge_fail(run_mock):
  run_mock.return_value = fake_CompletedProcess(1)

  with pytest_raises(Exception) as excinfo:
    merge(
      videoPath='tests/testFiles/test_merger/test_video.mp4',
      audioPath='tests/testFiles/test_merger/test_audio.m4a',
      outputDir='tests/testFiles/output/test_video_out.mp4',
      quiet=True
    )

  assert excinfo.type == Exception