from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from os.path import exists
from pymediainfo import MediaInfo
from dataclasses import dataclass

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.lazyYtDownload import lazyYtDownload
from src.service.MetaData import VideoMetaData, MetaDataOpt
from src.section.SubTitleSection import TSubtitleSectionRet
from src.section.OutputSection import TOutputSectionRet
from src.section.DownloadSection import DownloadOpt
from src.section.FormatSection import LazyFormatSectionRet
from src.structs.video_info import Subtitle
from src.structs.option import MediaType

@patch('src.lazyYtDownload.OutputSection.run')
@patch('src.lazyYtDownload.SubTitleSection.run')
@patch('src.lazyYtDownload.LazyFormatSection.run')
def test_setup (format_mock:Mock, subtitle_mock:Mock, output_mock:Mock):
  class fake_md (VideoMetaData):
    def __init__(self, *args, **kwargs):
      self.opts = MetaDataOpt()
    @property
    def title(self):
      return 'test title'

  @dataclass
  class Case:
    media : MediaType
    format_ls : list[str]
    do_write_subtitle : bool
    subtitle_ls : list[Subtitle]
    do_embed : bool
    do_burn : bool
    
  case_ls : list[Case] = [
    Case('Video', ['mp4'], True, [Subtitle('en', 'en', False)], True, False),
    Case('Audio', ['mp3'], False, [], False, False)
  ]
  
  for idx, case in enumerate(case_ls):
    print('testing case', idx)
    
    sub_ret :TSubtitleSectionRet = {
      'do_write_subtitle': case.do_write_subtitle,
      'subtitle_ls': case.subtitle_ls,
      'do_embed': case.do_embed,
      'do_burn': case.do_burn
    }
    output_ret :TOutputSectionRet = { 'dir': OUTPUT_FOLDER_PATH }
    
    format_mock.return_value = LazyFormatSectionRet(case.media, case.format_ls)
    subtitle_mock.return_value = sub_ret
    output_mock.return_value = output_ret

    md = fake_md()  
    setup_res = lazyYtDownload().setup([md])
    
    assert len(setup_res) == 1
    
    dl_opt = setup_res[0]
    assert dl_opt.media == case.media
    assert dl_opt.format == case.format_ls[0]
    if len(case.subtitle_ls) > 0:
      assert dl_opt.subtitle == case.subtitle_ls[0]
    else:
      assert dl_opt.subtitle is None
    assert dl_opt.embed_sub == case.do_embed
    assert dl_opt.burn_sub == case.do_burn
    assert dl_opt.output_dir == OUTPUT_FOLDER_PATH
    assert dl_opt.output_nm == md.title

@patch('src.section.LoginSection.LoginSection.run')
@patch('src.lazyYtDownload.lazyYtDownload.setup')
@patch('src.dl.UrlSection.run')
def test_download_yt_video_ng_(url_mock:Mock, setup_mock:Mock, login_mock:Mock):
  prepare_output_folder()

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  login_mock.return_value = None

  def fake_setup (md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    dl_opt = DownloadOpt(md_ls[0].opts)
    dl_opt.media = 'Video'
    dl_opt.format = 'mp4'
    dl_opt.set_subtitle(Subtitle('en', 'en', False), True, False)
    dl_opt.output_dir = OUTPUT_FOLDER_PATH
    dl_opt.output_nm = md_ls[0].title
    return [ dl_opt ]
  setup_mock.side_effect = fake_setup

  lazyYtDownload().run(loop=False)

  outputFile_path = f'{OUTPUT_FOLDER_PATH}/test video for videoDl.mp4'

  # check output file exist
  assert exists(outputFile_path)

  # check embed subtitle exist
  found_subtitle_track = False
  for track in MediaInfo.parse(outputFile_path).tracks:
    if track.track_type == 'Text':
      found_subtitle_track = True
      break
  assert found_subtitle_track

@patch('src.lazyYtDownload.lazyYtDownload.setup')
@patch('src.lazyYtDownload.lazyYtDownload.login')
@patch('src.dl.UrlSection.run')
def test_download_bili_video_ng_(url_mock:Mock, login_mock:Mock, setup_mock:Mock):
  prepare_output_folder()

  url_mock.return_value = 'https://www.bilibili.com/video/BV1154y1T765'
  login_mock.return_value = None

  def fake_setup (md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    dl_opt = DownloadOpt(md_ls[0].opts)
    dl_opt.media = 'Video'
    dl_opt.format = 'mp4'
    dl_opt.output_dir = OUTPUT_FOLDER_PATH
    dl_opt.output_nm = md_ls[0].title
    return [ dl_opt ]
  setup_mock.side_effect = fake_setup

  lazyYtDownload().run(loop=False)

  # check output file exist
  assert exists(f'{OUTPUT_FOLDER_PATH}/小 僧 觉 得 很 痛.mp4')
