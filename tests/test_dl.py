from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock
from os.path import exists

from tests.helpers import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.dl import Dl
from src.service.MetaData import VideoMetaData, MetaDataOpt
from src.section.DownloadSection import DownloadOpt
from src.section.SubTitleSection import TSubtitleSectionRet
from src.section.OutputSection import TOutputSectionRet
from src.structs.video_info import Subtitle


@patch('src.dl.DownloadSection')
@patch('src.dl.Dl.setup')
@patch('src.dl.Dl.get_metadata')
@patch('src.dl.Dl.login')
@patch('src.dl.UrlSection.run')
def test_download_call_count(
    url_mock:Mock, login_mock:Mock, md_mock:Mock, setup_mock:Mock, download_mock:Mock
  ):
  class fake_videoMd (VideoMetaData):
    def __init__ (self, *args, **kwargs):
      pass
  
  url_mock.return_value = ''
  login_mock.return_value = ''
  setup_mock.side_effect = lambda md_ls : [DownloadOpt() for _ in md_ls]

  # test video
  md_mock.return_value = [fake_videoMd()]
  Dl().run(loop=False)
  assert download_mock.call_count == 1

  # test playlist
  download_mock.reset_mock()
  md_mock.return_value = [fake_videoMd() for _ in range(3)]
  Dl().run(loop=False)
  assert download_mock.call_count == 3

@patch('src.dl.Dl.setup')
@patch('src.dl.LoginSection.run')
@patch('src.dl.UrlSection.run')
def test_run(url_mock:Mock, login_mock:Mock, setup_mock:Mock):
  """ test by a real run """
  def fake_setup(md_ls:list[VideoMetaData]) -> list[DownloadOpt]:
    dl_opt = DownloadOpt(md_ls[0].opts)
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
@patch('src.dl.ListFormatSection.run')
def test_setup (lsf_mock:Mock, format_mock:Mock, subtitle_mock:Mock, output_mock:Mock):
  lsf_mock.return_value = None
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
