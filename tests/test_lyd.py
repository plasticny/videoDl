from sys import path
path.append('src')

from unittest.mock import patch, call, ANY
from pytest import raises as pytest_raises

from uuid import uuid4
from os.path import exists
from pymediainfo import MediaInfo

from tests.testFileHelper import prepare_output_folder, OUTPUT_FOLDER_PATH

from src.lazyYtDownload import lazyYtDownload
from src.service.YtDlpHelper import Opts
from src.service.MetaData import VideoMetaData, PlaylistMetaData
from src.service.structs import Subtitle

# test login function
@patch('src.lazyYtDownload.LoginSection.run')
def test_login(login_mock):
  lyd = lazyYtDownload()

  # test other
  lyd.login('other', Opts())
  login_mock.assert_not_called()

  # test bilibili
  lyd.login('www.bilibili.com/video/BV1QK4y1d7dQ', Opts())
  login_mock.assert_called_once()

@patch('src.lazyYtDownload.lazyYtDownload.renameFile')
@patch('src.lazyYtDownload.Section')
@patch('src.lazyYtDownload.DownloadSection')
@patch('src.lazyYtDownload.listdir')
def test_download_subtitle(listdir_mock, download_section_mock, section_mock, _):
  """
    test the download function will download subtitle 
    if writeSubtitles or writeAutomaticSub is true
  """
  class fake_Section:
    def __init__(self, *args, **kwargs):
      pass
    def run(*args, **kwargs):
      pass
  class fake_videoMd(VideoMetaData):
    @property
    def title(self):
      return None
    @property
    def url(self):
      return None
    @property
    def audio_formats(self) -> list[dict]:
      return [{'ext': 'm4a'}]
    def __init__(self, *args, **kwargs):
      pass

  listdir_mock.return_value = ['filename.vtt']
  download_section_mock.side_effect = fake_Section
  section_mock.side_effect = fake_Section

  # test both false
  lazyYtDownload().download(Opts(), md=fake_videoMd())

  # test writeSubtitles is true
  opts = Opts()
  opts.setSubtitle(Subtitle('en', 'en', False))
  lazyYtDownload().download(opts, md=fake_videoMd()) 

  # test writeAutoSub is true
  opts = Opts()
  opts.setSubtitle(Subtitle('en', 'en', True))
  lazyYtDownload().download(opts, md=fake_videoMd()) 

  assert download_section_mock.mock_calls.count(
    call(title='Downloading subtitle', headerType=ANY)
  ) == 2

@patch('src.lazyYtDownload.lazyYtDownload.download_mp4')
@patch('src.lazyYtDownload.lazyYtDownload.download_separatly')
def test_download_flow(separatly_mock, mp4_mock):
  """
    Test the download function will
    call download_separatly when video has m4a audio format,
    or call download_mp4 when not
  """
  opts : Opts = Opts()
  opts.outputDir = OUTPUT_FOLDER_PATH
  opts.outputName = 'test.mp4'
  
  class fake_videoMd_m4a(VideoMetaData):
    @property
    def audio_formats(self) -> list[dict]:
      return ['m4a']
    def __init__(self, *args, **kwargs):
      pass
  class fake_videoMd_no_m4a(VideoMetaData):
    @property
    def audio_formats(self) -> list[dict]:
      return []
    def __init__(self, *args, **kwargs):
      pass

  # test m4a
  lazyYtDownload().download(opts, md=fake_videoMd_m4a())
  assert separatly_mock.called
  
  # test no m4a
  separatly_mock.reset_mock()
  mp4_mock.reset_mock()
  lazyYtDownload().download(opts, md=fake_videoMd_no_m4a())
  assert mp4_mock.called

@patch('src.lazyYtDownload.ffmpeg.output')
@patch('src.lazyYtDownload.ffmpeg.input')
def test_merge_subtitle(ffin_mock, ffout_mock):
  """test subtitle feature of merge function"""
  lyd = lazyYtDownload()

  # fake returned ffmpeg object of ffout_mock
  class FakeFfmpeg:
    def run(*args, **kwargs):
      pass
  ffout_mock.return_value = FakeFfmpeg()

  # test no subtitle
  ffin_mock.side_effect = [{'v':''},{'a':''}]
  lyd.merge('out.mp4', 'in.mp4', 'in.m4a', None, None)
  kwargs = ffout_mock.call_args.kwargs
  assert 'scodec' not in kwargs
  assert 'vf' not in kwargs

  # test embed subtitle
  ffin_mock.side_effect = [{'v':''},{'a':''},{'s':''}]
  lyd.merge('out.mp4', 'in.mp4', 'in.m4a', 'in.vtt', None, embedSubtitle=True)
  kwargs = ffout_mock.call_args.kwargs
  assert 'scodec' in kwargs
  assert 'vf' not in kwargs

  # test embed subtitle and burn subtitle
  ffin_mock.side_effect = [{'v':''},{'a':''},{'s':''}]
  lyd.merge('out.mp4', 'in.mp4', 'in.m4a', 'in.vtt', None, embedSubtitle=True, burnSubtitle=True)
  kwargs = ffout_mock.call_args.kwargs
  assert 'scodec' in kwargs
  assert 'vf' in kwargs

def test_renameFile_escape():
  """
    test renameFile function escape special char and rename file correctly
  """
  prepare_output_folder()

  # create a test file
  old_title = f'{str(uuid4())}.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{old_title}', 'w'):
    pass

  new_title = '"*:<>?|test.txt'
  expected_escape_title = 'test.txt'
  lazyYtDownload().renameFile(
    oldName=old_title, newName=new_title,
    dirPath=OUTPUT_FOLDER_PATH
  )

  assert not exists(f'{OUTPUT_FOLDER_PATH}\\{old_title}')
  assert exists(f'{OUTPUT_FOLDER_PATH}\\{expected_escape_title}')

def test_renameFile_overwrite():
  """
    test renameFile can overwrite file, if overwrite is true and file is exist
  """
  prepare_output_folder()

  # create a old file that will be rename
  old_title = 'old.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{old_title}', 'w') as f:
    f.write('old')
  
  # create a existed file that will be overwrite
  new_title = 'new.txt'
  with open(f'{OUTPUT_FOLDER_PATH}\\{new_title}', 'w') as f:
    f.write('new')

  # expect a error will be raise if not overwrite
  with pytest_raises(FileExistsError):
    lazyYtDownload().renameFile(
      oldName=old_title, newName=new_title,
      dirPath=OUTPUT_FOLDER_PATH,
      overwrite=False
    )

  # rename and overwrite
  lazyYtDownload().renameFile(
    oldName=old_title, newName=new_title,
    dirPath=OUTPUT_FOLDER_PATH,
    overwrite=True
  )

  # check file content
  assert not exists(f'{OUTPUT_FOLDER_PATH}\\{old_title}')
  assert exists(f'{OUTPUT_FOLDER_PATH}\\{new_title}')
  with open(f'{OUTPUT_FOLDER_PATH}\\{new_title}', 'r') as f:
    assert f.read() == 'old'

@patch('src.lazyYtDownload.lazyYtDownload.setup')
@patch('builtins.input')
def test_download_yt_video(input_mock, setup_mock):
  prepare_output_folder()

  input_mock.return_value = 'https://www.youtube.com/watch?v=JMu9kdGHU3A'

  opts = Opts()
  opts.outputDir = OUTPUT_FOLDER_PATH
  opts.setSubtitle(Subtitle('en', 'en', False))
  opts.embedSubtitle = True
  setup_mock.return_value = [opts]

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

@patch('builtins.input')
def test_download_bili_video(input_mock):
  def outputSection_faker(self, opts_ls:list[Opts], askDir:bool=True, askName:bool=True) -> Opts:
    ret = []
    for opts in opts_ls:
      opts = opts.copy()
      opts.outputDir = OUTPUT_FOLDER_PATH
      ret.append(opts)
    return ret
  def subtitleSection_faker(self, url, opts_ls:list[Opts]) -> Opts:
    ret = []
    for opts in opts_ls:
      opts = opts.copy()
      ret.append(opts)
    return [opts]
  
  prepare_output_folder()

  input_mock.side_effect = [
    'https://www.bilibili.com/video/BV1154y1T765', # url
    'N', # login
  ]
  outputSection_mock = patch('src.lazyYtDownload.OutputSection.run', outputSection_faker)
  subtitleSection_mock = patch('src.lazyYtDownload.SubTitleSection.run', subtitleSection_faker)
  with outputSection_mock, subtitleSection_mock:
    lazyYtDownload().run(loop=False)
  assert exists(f'{OUTPUT_FOLDER_PATH}/小 僧 觉 得 很 痛.mp4')