from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from pytest import raises as pytest_raises
from os.path import exists
from dataclasses import dataclass
from typing import Union
from uuid import uuid4

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.dl import Dl
from src.service.MetaData import VideoMetaData, MetaDataOpt, MetaData, PlaylistMetaData
from src.section.UrlSection import UrlSection
from src.section.DownloadSection import DownloadOpt
from src.section.SubTitleSection import TSubtitleSectionRet
from src.section.OutputSection import TOutputSectionRet
from src.structs.video_info import Subtitle


@patch('src.dl.DownloadSection')
@patch('src.dl.Dl.setup')
@patch('src.dl.Dl.get_metadata')
@patch('src.dl.Dl.login')
@patch('src.dl.UrlSection')
def test_download_call_count(
    url_mock:Mock, login_mock:Mock, md_mock:Mock, setup_mock:Mock, download_mock:Mock
  ):
  """ test run working by checking times of download called """
  class fake_videoMd (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  
  class fake_UrlSection (UrlSection):
    def __init__ (self, *args, **kwargs):
      pass
    def run (self):
      return ''
  
  @dataclass
  class Case:
    md_ret_ls : Union[list[MetaData], None]
    do_md_failed : bool
    expected_call_count : int
  
  video_md = fake_videoMd()
  
  url_mock.return_value = fake_UrlSection()
  login_mock.return_value = ''
  setup_mock.side_effect = lambda md_ls : [DownloadOpt() for _ in md_ls]
  
  case_ls : list[Case] = [
    Case([video_md], False, 1),
    Case([video_md, video_md], False, 2),
    Case(None, True, 0)
  ]
    
  for idx, case in enumerate(case_ls):
    print('testing case', idx + 1)
    
    download_mock.reset_mock()
    
    if case.do_md_failed:
      md_mock.side_effect = Exception()
      with pytest_raises(Exception) as e_info:
        Dl().run(loop=False)
        assert 'Download Failed, error on getting url info' in str(e_info.value)
    else:
      md_mock.return_value = case.md_ret_ls
      Dl().run(loop=False)

    assert download_mock.call_count == case.expected_call_count

@patch('src.dl.Dl.setup')
@patch('src.dl.LoginSection.run')
@patch('src.dl.UrlSection.run')
def test_run(url_mock:Mock, login_mock:Mock, setup_mock:Mock):
  """ test by a real run """
  def fake_setup(md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    dl_opt = DownloadOpt(md_ls[0].opts)
    dl_opt.media = 'Video'
    dl_opt.output_dir = OUTPUT_FOLDER_PATH
    dl_opt.format = 'mp4'
    dl_opt.output_nm = md_ls[0].title
    return [ dl_opt ]

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  login_mock.return_value = None
  setup_mock.side_effect = fake_setup

  prepare_output_folder()
  Dl().run(loop=False)

  assert exists(f'{OUTPUT_FOLDER_PATH}/test video for videoDl.mp4')

@patch('src.dl.OutputSection.run')
@patch('src.dl.SubTitleSection.run')
@patch('src.dl.FormatSection.run')
def test_setup (format_mock:Mock, subtitle_mock:Mock, output_mock:Mock):
  format_mock.return_value = 'mp4'
  
  ret_subtitle : TSubtitleSectionRet = {
    'do_write_subtitle': True,
    'subtitle_ls': [Subtitle('en', 'en', False)],
    'do_embed': True,
    'do_burn': False
  }
  subtitle_mock.return_value = ret_subtitle
  
  ret_output :TOutputSectionRet = { 'dir': OUTPUT_FOLDER_PATH }
  output_mock.return_value = ret_output
  
  class fake_md (VideoMetaData):
    @property
    def title(self):
      return 'test title'
    def __init__(self, *args, **kwargs):
      self.opts = MetaDataOpt()
      pass
  setup_res = Dl().setup([fake_md()])
  
  assert len(setup_res) == 1
  
  dl_opt = setup_res[0]
  assert dl_opt.format == 'mp4'
  assert dl_opt.subtitle == ret_subtitle['subtitle_ls'][0]
  assert dl_opt.embed_sub == ret_subtitle['do_embed']
  assert dl_opt.burn_sub == ret_subtitle['do_burn']
  assert dl_opt.output_dir == ret_output['dir']
  assert dl_opt.output_nm == 'test title'

@patch('src.dl.fetchMetaData')
def test_get_metadata (fetch_md_mock:Mock):
  class fake_VideoMetaData (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  
  class fake_PlaylistMetaData (PlaylistMetaData):
    def __init__ (self, videos:list[VideoMetaData]):
      self.videos = videos
  
  @dataclass
  class Case:
    fetched_md : Union[MetaData, None]
    expected : Union[list[VideoMetaData], None]
  
  url = uuid4().__str__()
  cookie_file_path = uuid4().__str__()
  
  video_md1 = fake_VideoMetaData()
  video_md2 = fake_VideoMetaData()
  playlist_md = fake_PlaylistMetaData([video_md1, video_md2])
  
  case_ls : list[Case] = [
    Case(video_md1, [video_md1]),
    Case(playlist_md, [video_md1, video_md2]),
    Case(None, None) # fetch failed
  ]
  
  for idx, case in enumerate(case_ls):
    print('testing case', idx + 1)
    
    fetch_md_mock.reset_mock()
    fetch_md_mock.return_value = case.fetched_md
    
    if case.fetched_md is None:
      with pytest_raises(Exception) as e_info:
        Dl().get_metadata(url, cookie_file_path)
        assert str(e_info.value) == 'Failed to get video metadata'
    else:
      md_ls = Dl().get_metadata(url, cookie_file_path)
      assert md_ls == case.expected
    
    # check fetchMetaData call
    assert fetch_md_mock.call_count == 1
    opt = fetch_md_mock.call_args[0][0]
    assert opt.url == url
    assert opt.cookie_file_path == cookie_file_path
    