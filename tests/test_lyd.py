from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from os.path import exists
from pymediainfo import MediaInfo
from dataclasses import dataclass
from uuid import uuid4
from typing import Optional

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.lazyYtDownload import lazyYtDownload
from src.service.MetaData import VideoMetaData, MetaDataOpt
from src.section.SubTitleSection import TSubtitleSectionRet
from src.section.OutputSection import TOutputSectionRet
from src.section.DownloadSection import DownloadOpt
from src.section.FormatSection import LazyFormatSectionRet
from src.section.LoginSection import LoginSectionRet
from src.structs.video_info import Subtitle
from src.structs.option import MediaType

@patch('src.lazyYtDownload.OutputSection.run')
@patch('src.lazyYtDownload.SubTitleSection.run')
@patch('src.lazyYtDownload.LazyFormatSection.run')
def test_setup (format_mock:Mock, subtitle_mock:Mock, output_mock:Mock):
  def random_str ():
    return str(uuid4())

  class fake_md (VideoMetaData):
    def __init__(self, title, *args, **kwargs):
      self.opts = MetaDataOpt()
      self._title = title
    @property
    def title(self):
      return self._title

  @dataclass
  class Case:
    # input
    md_ls: list[VideoMetaData]
    # mock format select
    media : MediaType
    format_ls : list[str]
    sort_ls: list[Optional[str]]
    # mock subtitle select
    do_write_subtitle : bool
    subtitle_ls : list[Subtitle]
    do_embed : bool
    do_burn : bool

  md1 = fake_md('test1')
  md2 = fake_md('test2')
  format_str1 = random_str()
  format_str2 = random_str()
  sort_str1 = random_str()
  sort_str2 = random_str()
  sub1 = Subtitle(random_str(), random_str(), False)
  sub2 = Subtitle(random_str(), random_str(), False)

  case_ls : list[Case] = [
    Case(
      [md1, md2],
      'Video', [format_str1, format_str2], [sort_str1, sort_str2],
      True, [sub1, sub2], True, False
    ),
    Case(
      [md1],
      'Audio', [format_str1], [None],
      False, [], False, False
    )
  ]
  
  for case_idx, case in enumerate(case_ls):
    print('testing case', case_idx)
    
    sub_ret :TSubtitleSectionRet = {
      'do_write_subtitle': case.do_write_subtitle,
      'subtitle_ls': case.subtitle_ls,
      'do_embed': case.do_embed,
      'do_burn': case.do_burn
    }
    output_ret :TOutputSectionRet = { 'dir': random_str() }
    
    format_mock.return_value = LazyFormatSectionRet(case.media, case.format_ls, case.sort_ls)
    subtitle_mock.return_value = sub_ret
    output_mock.return_value = output_ret

    setup_res = lazyYtDownload().setup(case.md_ls)
    
    assert len(setup_res) == len(case.md_ls)
    for ret_idx, ret in enumerate(setup_res):
      assert ret.media == case.media
      assert ret.format == case.format_ls[ret_idx]
      assert ret.sorting == case.sort_ls[ret_idx]
      if len(case.subtitle_ls) > 0:
        assert ret.subtitle == case.subtitle_ls[ret_idx]
      else:
        assert ret.subtitle is None
      assert ret.embed_sub == case.do_embed
      assert ret.burn_sub == case.do_burn
      assert ret.output_dir == output_ret['dir']
      assert ret.output_nm == case.md_ls[ret_idx].title

@patch('src.section.LoginSection.LoginSection.run')
@patch('src.lazyYtDownload.lazyYtDownload.setup')
@patch('src.dl.UrlSection.run')
def test_download_yt_video_ng_(url_mock:Mock, setup_mock:Mock, login_mock:Mock):
  prepare_output_folder()

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'
  login_mock.return_value = LoginSectionRet(False)

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
  login_mock.return_value = LoginSectionRet(False)

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
