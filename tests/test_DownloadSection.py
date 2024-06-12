from sys import path
from pathlib import Path

from src.structs.option import IOpt
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock, call as mock_call
from pytest import raises as pytest_raises
from os.path import exists
from uuid import uuid4
from typing_extensions import Union, Literal
from dataclasses import dataclass
from random import randint

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.section.DownloadSection import DownloadSection, DownloadOpt, BundledTDownloadOpt
from src.service.fileHelper import TEMP_FOLDER_PATH, perpare_temp_folder, clear_temp_folder
from src.structs.video_info import Subtitle, BundledFormat
from src.structs.option import MediaType


@patch('src.section.DownloadSection.YoutubeDL.download')
def test_with_fail_download(download_mock):
  # make download fail
  download_mock.side_effect = Exception()

  with pytest_raises(Exception):
    DownloadSection()._download_item('invalid url', {}, retry=2)  

  # check if download is called 3 times
  assert download_mock.call_count == 3

@patch('src.section.DownloadSection.DownloadSection._download_audio')
@patch('src.section.DownloadSection.DownloadSection._download_video')
def test_main (video_mock : Mock, audio_mock : Mock):
  @dataclass
  class Case:
    media : MediaType
    video_called : bool
    audio_called : bool
    @property
    def opt (self):
      res = DownloadOpt()
      res.media = self.media
      return res
    
  video_mock.return_value = None
  audio_mock.return_value = None
    
  case_ls : list[Case] = [
    Case('Video', video_called=True, audio_called=False),
    Case('Audio', video_called=False, audio_called=True)
  ]
  for case in case_ls:
    print('testing', case.media)
    
    video_mock.reset_mock()
    audio_mock.reset_mock()
    
    DownloadSection().run(case.opt)
    
    assert video_mock.called == case.video_called
    assert audio_mock.called == case.audio_called

    mock_called = video_mock if video_mock.called else audio_mock
    assert mock_called.call_args[0][0].media == case.media
    assert mock_called.call_args[0][1] == 0

@patch('src.section.DownloadSection.DownloadSection._move_temp_file')
@patch('src.section.DownloadSection.DownloadSection._merge')
@patch('src.section.DownloadSection.DownloadSection._download_item')
@patch('src.section.DownloadSection.DownloadOpt.to_ytdlp_sub_opt')
@patch('src.section.DownloadSection.DownloadOpt.to_ytdlp_dl_opt')
def test_download_video(
  to_dl_opt_mock:Mock, to_sub_opt_mock:Mock,
  download_mock:Mock, merge_mock:Mock, move_mock:Mock
):
  """
    test the download flow when:\n
    1. the download option is bundled and not bundled\n
    2. add and not add subtitle\n
    3. merge or not
  """
  # fake basic setting
  fake_url = 'url'
  fake_downloaded_file_nm = 'downloaded file name'
  # fake non-bundled download option
  fake_dl_opt = { "outtmpl": { "default": "" } }
  # fake bundled download option
  fake_bundled_v = { 'v': 'v' }
  fake_bundled_a = { 'a': 'a' }
  fake_bundled_dl_opt = BundledTDownloadOpt(video=fake_bundled_v, audio=fake_bundled_a)
  # fake subtitle
  fake_sub_lang = 'en'
  
  # [(fake download option, subtitleslangs list in fake subtitle option)]
  case_ls : list[tuple[Union[dict, BundledTDownloadOpt], list[str]]] = [
    # not bundled, no subtitle
    (fake_dl_opt, []),
    # bundled, no subtitle
    (fake_bundled_dl_opt, []),
    # not bundled, has subtitle
    (fake_dl_opt, [fake_sub_lang]),
  ]
  
  for case in case_ls:
    print('testing', case)
    case_dl_opt, case_sub_langs = case
    case_sub_opt = { 'subtitleslangs': case_sub_langs }
    
    # reset mock
    download_mock.reset_mock()
    merge_mock.reset_mock()
    move_mock.reset_mock()
    
    # mock
    download_mock.return_value = fake_downloaded_file_nm
    to_dl_opt_mock.return_value = case_dl_opt
    to_sub_opt_mock.return_value = case_sub_opt

    opts = DownloadOpt()
    opts.url = fake_url
    
    is_bundle = isinstance(case_dl_opt, BundledTDownloadOpt)
    has_sub = len(case_sub_langs) > 0
    
    # expected download call
    expected_download_calls = []
    if is_bundle:
      expected_download_calls.append(mock_call(fake_url, fake_bundled_v, 0))
      expected_download_calls.append(mock_call(fake_url, fake_bundled_a, 0))
    else:
      expected_download_calls.append(mock_call(fake_url, case_dl_opt, 0))
      
    if has_sub:
      expected_download_calls.append(mock_call(fake_url, case_sub_opt, 0))

    DownloadSection()._download_video(opts, retry=0)

    download_calls = download_mock.mock_calls.copy()
    assert len(download_calls) == len(expected_download_calls)
    for call in download_calls:
      assert call in expected_download_calls

    if is_bundle or has_sub:
      assert merge_mock.call_count == 1
      
    move_mock.assert_called()

@patch('src.section.DownloadSection.DownloadSection._move_temp_file')
@patch('src.section.DownloadSection.run_ffmpeg')
@patch('src.section.DownloadSection.get_audio_sample_rate')
@patch('src.section.DownloadSection.DownloadSection._download_item')
@patch('src.section.DownloadSection.DownloadOpt.to_ytdlp_dl_opt')
def test_download_audio (
  opt_mock : Mock,
  download_mock : Mock, audio_sample_mock : Mock,
  ffmpeg_mock : Mock, move_mock : Mock
):
  class fake_DownloadOpt (DownloadOpt):
    def __init__(self, url : str):
      self._url = url
      self.output_dir = uuid4().__str__()
      self.output_nm = uuid4().__str__()
    @property
    def url (self):
      return self._url
  
  fake_opts = fake_DownloadOpt(url = uuid4().__str__())
  fake_retry = randint(0, 10)
  fake_dl_opt = Mock()
  fake_item_nm = uuid4().__str__()
  fake_sample_rate = randint(0, 90000)
  
  opt_mock.return_value = fake_dl_opt
  download_mock.return_value = fake_item_nm
  audio_sample_mock.return_value = fake_sample_rate
  ffmpeg_mock.return_value = None
  move_mock.return_value = None
  
  DownloadSection()._download_audio(fake_opts, fake_retry)
  
  assert download_mock.mock_calls == [mock_call(fake_opts.url, fake_dl_opt, fake_retry)]
  assert audio_sample_mock.mock_calls == [mock_call(f'{TEMP_FOLDER_PATH}/{fake_item_nm}')]
  assert ffmpeg_mock.called
  assert move_mock.call_args.kwargs['out_dir'] == fake_opts.output_dir
  assert f'{fake_opts.output_nm}.' in move_mock.call_args.kwargs['out_nm']

@patch('src.section.DownloadSection.YoutubeDL')
def test_download_item (ytdl_mock:Mock):
  """ test the function return the file full name """
  prepare_output_folder()
  
  class fake_ytdlp ():
    def __init__(self, *args, **kwargs):
      pass
    def download(self, *args):
      open(f'{OUTPUT_FOLDER_PATH}/{temp_nm}.mp4', 'w')
  ytdl_mock.side_effect = fake_ytdlp
  
  temp_nm = uuid4().__str__()
  fake_opts = {
    'paths': { 'home': OUTPUT_FOLDER_PATH },
    'outtmpl': f'{temp_nm}.%(ext)s'
  }
  
  ret_name =  DownloadSection()._download_item('url', fake_opts, retry=0)
  assert ret_name == f'{temp_nm}.mp4'
  
@patch('src.section.DownloadSection.run_ffmpeg')
@patch('src.section.DownloadSection.ff_in')
def test_merge_subtitle(ffin_mock:Mock, run_ffmpeg_mock:Mock):
  """test subtitle feature of merge function"""
  fake_ff_in_v = {'v': ''}
  fake_ff_in_a = {'a': ''}
  fake_ff_in_s = {'s': ''}
  fake_video_path = 'in.mp4'
  fake_audio_path = 'in.m4a'
  fake_subtitle_path = 'in.vtt'
  
  run_ffmpeg_mock.return_value = None
  
  # [(list of ff_in return, do_embed_sub, do_burn_sub, expected key of kwargs in ff_out call)]
  case_ls : list[tuple[list[dict], bool, bool, list[str]]] = [
    # test no subtitle
    ([fake_ff_in_v, fake_ff_in_a], False, False, []),
    # test embed subtitle
    ([fake_ff_in_v, fake_ff_in_a, fake_ff_in_s], True, False, ['scodec']),
    # test embed subtitle and burn subtitle
    ([fake_ff_in_v, fake_ff_in_a, fake_ff_in_s], True, True, ['scodec', 'vf'])
  ]
  
  for case in case_ls:
    print('testing', case)
    case_ff_in_side_effect, case_do_embed_sub, case_do_burn_sub, case_expected_keys = case
    
    ffin_mock.reset_mock()
    run_ffmpeg_mock.reset_mock()
    
    ffin_mock.side_effect = case_ff_in_side_effect
    
    DownloadSection()._merge(
      fake_video_path, fake_audio_path, fake_subtitle_path,
      do_embed_sub=case_do_embed_sub, do_burn_sub=case_do_burn_sub
    )
    
    for key in case_expected_keys:
      assert key in run_ffmpeg_mock.call_args[0][1]
  
def test_move_temp_file():
  """
    test _move_temp_file function:
    1. escape special char
    2. rename file correctly
    3. move file to correct folder
  """
  perpare_temp_folder()
  clear_temp_folder()
  
  prepare_output_folder()

  # create a test file
  temp_nm = f'{uuid4().__str__()}'
  open(f'{TEMP_FOLDER_PATH}/{temp_nm}', 'w')

  out_nm = '"*:<>?|test'
  expected_name = 'test'
  DownloadSection()._move_temp_file(
    temp_nm=temp_nm,
    out_dir=OUTPUT_FOLDER_PATH, out_nm=out_nm
  )

  assert not exists(f'{OUTPUT_FOLDER_PATH}/{temp_nm}')
  assert exists(f'{OUTPUT_FOLDER_PATH}/{expected_name}')


# ========== Download option ========== #
@patch('src.section.DownloadSection.uuid4')
def test_downloadOpt_to_base_opt (uuid4_mock:Mock):
  """
    test the result opt has random name,\n
    and set the path to the temp folder
  """
  temp_nm = 'temp_nm'
  uuid4_mock.return_value = temp_nm
  
  opts = DownloadOpt()
  opts.url = 'url'
  opts.output_dir = 'output_dir'
  opts.output_nm = 'output_nm'
  
  base_opt = DownloadOpt.to_ytdlp_base_opt(opts)
  assert base_opt['outtmpl'] == f'{temp_nm}.%(ext)s'
  assert base_opt['paths']['home'] == TEMP_FOLDER_PATH

def test_downloadOpt_to_dl_opt ():
  """
    test the function return correct type of opt\n
    For type BundledTDownloadOpt, check video and audio have different name
  """
  fake_url = 'url'
  fake_output_dir = 'output_dir'
  fake_format = 'format'
  fake_bundled_format = BundledFormat('v', 'a')
  
  # [(format, expected is bundled)]
  case_ls : list[Union[str, BundledFormat]] = [
    # not bundled
    fake_format,
    # bundled
    fake_bundled_format
  ]
  
  for case_format in case_ls:
    print('testing', case_format)
    opts = DownloadOpt()
    opts.url = fake_url
    opts.output_dir = fake_output_dir
    opts.format = case_format
    
    dl_opt = DownloadOpt.to_ytdlp_dl_opt(opts)
    
    if isinstance(case_format, BundledFormat):
      assert isinstance(dl_opt, BundledTDownloadOpt)
      assert dl_opt.video['format'] == case_format.video
      assert dl_opt.audio['format'] == case_format.audio
    else:
      assert not isinstance(dl_opt, BundledTDownloadOpt)
      assert dl_opt['format'] == case_format

def test_downloadOpt_to_sub_opt():
  """
    Check the returned opt has all the required fields,\n
    and set the fields correctly
  """
  fake_url = 'url'
  fake_output_dir = 'output_dir'
  fake_sub1 = Subtitle('en', 'en', False)
  fake_sub2 = Subtitle('cn', 'cn', True)
  
  # [subtitle in option]
  case_ls : list[Subtitle] = [
    # no subtitle
    None,
    # not auto subtitle
    fake_sub1,
    # auto subtitle
    fake_sub2
  ]
  
  for case_sub in case_ls:
    print('testing', case_sub)
    opts = DownloadOpt()
    opts.url = fake_url
    opts.output_dir = fake_output_dir
    opts.subtitle = case_sub

    sub_opt = DownloadOpt.to_ytdlp_sub_opt(opts)

    if case_sub is None:
      assert sub_opt['writesubtitles'] == False
      assert sub_opt['writeautomaticsub'] == False
      assert sub_opt['subtitleslangs'] == []
      assert sub_opt['skip_download'] == True
    else:
      assert sub_opt['writesubtitles'] == (not case_sub.isAuto)
      assert sub_opt['writeautomaticsub'] == case_sub.isAuto
      assert sub_opt['subtitleslangs'] == [case_sub.code]
      assert sub_opt['skip_download'] == True
# ========== Download option ========== #
