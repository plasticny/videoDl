from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from random import randint
from uuid import uuid4
from dataclasses import dataclass
from typing import Union

from unittest.mock import patch, Mock, call as mock_call

from src.service.ffmpeg_helper import run_ffmpeg, get_audio_sample_rate

@patch('src.service.ffmpeg_helper.ff_out')
def test_run_ffmpeg (ff_out_mock : Mock):
  class fake_ff_out_ret:
    def run (self, cmd : str):
      pass
  ff_out_mock.return_value = fake_ff_out_ret()
  
  stream_n_output = [randint(0, 100) for _ in range(10)]
  kwargs = {str(uuid4()) : randint(0, 100) for _ in range(10)}
  
  run_ffmpeg(stream_n_output, kwargs)
  
  assert ff_out_mock.mock_calls[0] == mock_call(*stream_n_output, **kwargs)

def test_get_streams ():
  # cause its implementation is copied from ffprobe-python module
  # so it's not worth to test it
  pass

@patch('src.service.ffmpeg_helper.get_streams')
def test_get_audio_sample_rate (get_streams_mock : Mock):
  @dataclass
  class fake_Stream:
    is_audio : bool
    sample_rate : Union[int, None]
  
  @dataclass
  class Case:
    streams : list[fake_Stream]
    expected : Union[int, None]
    
  video_stream : fake_Stream = fake_Stream(is_audio = False, sample_rate = None)
  audio_stream : fake_Stream = fake_Stream(is_audio = True, sample_rate = 44100)
    
  case_ls : list[Case] = [
    Case(
      streams = [video_stream, audio_stream],
      expected = audio_stream.sample_rate
    ),
    Case(
      streams = [video_stream],
      expected = None
    )
  ]
  
  for case in case_ls:
    get_streams_mock.return_value = case.streams
    assert get_audio_sample_rate('') == case.expected
