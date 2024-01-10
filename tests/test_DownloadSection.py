from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock, call
from pytest import raises as pytest_raises
from os.path import exists
from uuid import uuid4

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.section.DownloadSection import DownloadSection, DownloadOpt, BundledTDownloadOpt
from src.service.fileHelper import TEMP_FOLDER_PATH
from src.structs.video_info import Subtitle, BundledFormat


@patch('src.section.DownloadSection.YoutubeDL.download')
def test_with_fail_download(download_mock):
  # make download fail
  download_mock.side_effect = Exception()

  with pytest_raises(Exception):
    DownloadSection()._download_item('invalid url', {}, retry=2)  

  # check if download is called 3 times
  assert download_mock.call_count == 3

@patch('src.section.DownloadSection.DownloadSection._move_temp_file')
@patch('src.section.DownloadSection.DownloadSection._merge')
@patch('src.section.DownloadSection.DownloadSection._download_item')
@patch('src.section.DownloadSection.DownloadOpt.to_ytdlp_sub_opt')
@patch('src.section.DownloadSection.DownloadOpt.to_ytdlp_dl_opt')
def test_main_flow(
  to_dl_opt_mock:Mock, to_sub_opt_mock:Mock,
  download_mock:Mock, merge_mock:Mock, move_mock:Mock
):
  """
    test the download flow when:\n
    1. the download option is bundled and not bundled\n
    2. add and not add subtitle\n
    3. merge or not
  """
  opts = DownloadOpt()
  opts.url = 'url'
  
  ret_dl_opt = { "outtmpl": { "default": "" } }
  bundled_v = { 'v': 'v' }
  bundled_a = { 'a': 'a' }
  ret_bundled_dl_opt = BundledTDownloadOpt(video=bundled_v, audio=bundled_a)
  ret_sub_opt = { 'sub': 'sub' }
  
  download_mock.return_value = 'downloaded file name'
    
  # === test the flow in different `is_bundle` === #
  opts.subtitle = None
  to_sub_opt_mock.return_value = ret_sub_opt
  
  # is_bundle = False
  to_dl_opt_mock.return_value = ret_dl_opt
  DownloadSection().run(opts, retry=0)
  download_calls = download_mock.mock_calls.copy()
  assert len(download_calls) == 1
  assert download_calls[0] == call('url', ret_dl_opt, 0)
  assert len(merge_mock.mock_calls) == 0
  
  # is_bundle = True
  download_mock.reset_mock()
  merge_mock.reset_mock()
  to_dl_opt_mock.return_value = ret_bundled_dl_opt
  DownloadSection().run(opts, retry=0)
  download_calls = download_mock.mock_calls.copy()
  assert len(download_calls) == 2
  assert download_calls[0] == call('url', bundled_v, 0)
  assert download_calls[1] == call('url', bundled_a, 0)
  assert len(merge_mock.mock_calls) == 1
  
  # === test the flow in different `has_sub` === #
  to_dl_opt_mock.return_value = ret_dl_opt
  to_sub_opt_mock.return_value = ret_sub_opt
  
  # has_sub = False
  # already tested above
  
  # has_sub = True
  download_mock.reset_mock()
  merge_mock.reset_mock()
  opts.subtitle = Subtitle('en', 'en', False)
  DownloadSection().run(opts, retry=0)
  download_calls = download_mock.mock_calls.copy()
  assert len(download_calls) == 2
  assert download_calls[0] == call('url', ret_dl_opt, 0)
  assert download_calls[1] == call('url', ret_sub_opt, 0)
  assert len(merge_mock.mock_calls) == 1

@patch('src.section.DownloadSection.YoutubeDL.download')
def test_download_item (download_mock:Mock):
  """ test the function return the file full name """
  temp_nm = uuid4().__str__()
  fake_opts = {
    'paths': { 'home': OUTPUT_FOLDER_PATH },
    'outtmpl': f'{temp_nm}.%(ext)s'
  }
  
  def fake_download (*args):
    with open(f'{OUTPUT_FOLDER_PATH}/{temp_nm}.mp4', 'w'):
      pass
  download_mock.side_effect = fake_download
  
  ret_name =  DownloadSection()._download_item('url', fake_opts, retry=0)
  assert ret_name == f'{temp_nm}.mp4'
  
@patch('src.section.DownloadSection.ff_out')
@patch('src.section.DownloadSection.ff_in')
def test_merge_subtitle(ffin_mock:Mock, ffout_mock:Mock):
  """test subtitle feature of merge function"""
  section = DownloadSection()

  # fake returned ffmpeg object of ffout_mock
  class FakeFfmpeg:
    def run(*args, **kwargs):
      pass
  ffout_mock.return_value = FakeFfmpeg()

  # test no subtitle
  ffin_mock.side_effect = [{'v':''},{'a':''}]
  section._merge('in.mp4', 'in.m4a', None)
  kwargs = ffout_mock.call_args.kwargs
  assert 'scodec' not in kwargs
  assert 'vf' not in kwargs

  # test embed subtitle
  ffout_mock.reset_mock()
  ffin_mock.side_effect = [{'v':''},{'a':''},{'s':''}]
  section._merge('in.mp4', 'in.m4a', 'in.vtt', do_embed_sub=True)
  kwargs = ffout_mock.call_args.kwargs
  assert 'scodec' in kwargs
  assert 'vf' not in kwargs

  # test embed subtitle and burn subtitle
  ffout_mock.reset_mock()
  ffin_mock.side_effect = [{'v':''},{'a':''},{'s':''}]
  section._merge('in.mp4', 'in.m4a', 'in.vtt', do_embed_sub=True, do_burn_sub=True)
  kwargs = ffout_mock.call_args.kwargs
  assert 'scodec' in kwargs
  assert 'vf' in kwargs
  
def test_move_temp_file():
  """
    test _move_temp_file function:
    1. escape special char
    2. rename file correctly
    3. move file to correct folder
  """
  prepare_output_folder()

  # create a test file
  temp_nm = f'{uuid4().__str__()}'
  with open(f'{TEMP_FOLDER_PATH}\\{temp_nm}', 'w'):
    pass

  out_nm = '"*:<>?|test'
  expected_name = 'test'
  DownloadSection()._move_temp_file(
    temp_nm=temp_nm,
    out_dir=OUTPUT_FOLDER_PATH, out_nm=out_nm
  )

  assert not exists(f'{OUTPUT_FOLDER_PATH}\\{temp_nm}')
  assert exists(f'{OUTPUT_FOLDER_PATH}\\{expected_name}.mp4')


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
  # test not bundled
  opts = DownloadOpt()
  opts.url = 'url'
  opts.output_dir = 'output_dir'
  opts.format = 'format'
  
  dl_opt = DownloadOpt.to_ytdlp_dl_opt(opts)
  assert not isinstance(dl_opt, BundledTDownloadOpt)
  
  # test bundled
  opts.format = BundledFormat('v', 'a')
  
  dl_opt = DownloadOpt.to_ytdlp_dl_opt(opts)
  assert isinstance(dl_opt, BundledTDownloadOpt)
  assert dl_opt.video['outtmpl'] != dl_opt.audio['outtmpl']

def test_downloadOpt_to_sub_opt():
  """
    Check the returned opt has all the required fields,\n
    and set the fields correctly
  """
  opts = DownloadOpt()
  opts.url = 'url'
  opts.output_dir = 'output_dir'
  
  # test no subtitle
  opts.subtitle = None
  sub_opt = DownloadOpt.to_ytdlp_sub_opt(opts)
  assert sub_opt['writesubtitles'] == False
  assert sub_opt['writeautomaticsub'] == False
  assert sub_opt['subtitleslangs'] == []
  assert sub_opt['skip_download'] == True
  
  # == test subtitle == #
  # not auto subtitle
  opts.subtitle = Subtitle('en', 'en', False)
  sub_opt = DownloadOpt.to_ytdlp_sub_opt(opts)
  assert sub_opt['writesubtitles'] == True
  assert sub_opt['writeautomaticsub'] == False
  assert sub_opt['subtitleslangs'] == ['en']
  assert sub_opt['skip_download'] == True
  
  # auto subtitle
  opts.subtitle = Subtitle('cn', 'cn', True)
  sub_opt = DownloadOpt.to_ytdlp_sub_opt(opts)
  assert sub_opt['writesubtitles'] == False
  assert sub_opt['writeautomaticsub'] == True
  assert sub_opt['subtitleslangs'] == ['cn']
  assert sub_opt['skip_download'] == True
# ========== Download option ========== #
