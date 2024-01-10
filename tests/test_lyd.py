from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from os.path import exists
from pymediainfo import MediaInfo

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.lazyYtDownload import lazyYtDownload
from src.service.MetaData import VideoMetaData, MetaDataOpt
from src.section.SubTitleSection import TSubtitleSectionRet
from src.section.OutputSection import TOutputSectionRet
from src.section.DownloadSection import DownloadOpt
from src.structs.video_info import Subtitle

# test login function
@patch('src.dl.LoginSection.run')
def test_login(login_mock:Mock):
  lyd = lazyYtDownload()

  # test other
  lyd.login('other')
  login_mock.assert_not_called()

  # test bilibili
  login_mock.reset_mock()
  lyd.login('www.bilibili.com/video/BV1QK4y1d7dQ')
  login_mock.assert_called_once()

@patch('src.lazyYtDownload.OutputSection.run')
@patch('src.lazyYtDownload.SubTitleSection.run')
@patch('src.lazyYtDownload.LazyFormatSection.run')
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
  setup_res = lazyYtDownload().setup([fake_md()])
  
  assert len(setup_res) == 1
  
  dl_opt = setup_res[0]
  assert dl_opt.format == 'mp4'
  assert dl_opt.subtitle == ret_subtitle['subtitle_ls'][0]
  assert dl_opt.embed_sub == ret_subtitle['do_embed']
  assert dl_opt.burn_sub == ret_subtitle['do_burn']
  assert dl_opt.output_dir == ret_output['dir']
  assert dl_opt.output_nm == 'test title'

@patch('src.lazyYtDownload.lazyYtDownload.setup')
@patch('src.dl.UrlSection.run')
def test_download_yt_video(url_mock:Mock, setup_mock:Mock):
  prepare_output_folder()

  url_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'

  def fake_setup (md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    dl_opt = DownloadOpt(md_ls[0].opts)
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
def test_download_bili_video(url_mock:Mock, login_mock:Mock, setup_mock:Mock):
  prepare_output_folder()

  url_mock.return_value = 'https://www.bilibili.com/video/BV1154y1T765'
  login_mock.return_value = None

  def fake_setup (md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    dl_opt = DownloadOpt(md_ls[0].opts)
    dl_opt.format = 'mp4'
    dl_opt.output_dir = OUTPUT_FOLDER_PATH
    dl_opt.output_nm = md_ls[0].title
    return [ dl_opt ]
  setup_mock.side_effect = fake_setup

  lazyYtDownload().run(loop=False)

  # check output file exist
  assert exists(f'{OUTPUT_FOLDER_PATH}/小 僧 觉 得 很 痛.mp4')