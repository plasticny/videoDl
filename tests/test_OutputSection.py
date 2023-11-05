from sys import path
path.append('src')

from unittest.mock import patch, call

from src.section.OutputSection import OutputSection, Message
from src.service.YtDlpHelper import Opts

def test_all_not_ask():
  opts = OutputSection('').run(askDir=False, askName=False, opts=Opts())
  assert opts()['paths'] == {}
  assert opts()['outtmpl'] == None

@patch('tkinter.filedialog.askdirectory')
@patch('builtins.print')
def test_askOutputDir(print_mock, askdirectory_mock):
  output_section = OutputSection('Test')

  # First test with invalid directory, then with valid directory
  valid_dir = '/path/to/output/dir'
  askdirectory_mock.side_effect = ['', valid_dir]
  
  opts = output_section.run(askDir=True, askName=False, opts=Opts())

  print_mock.mock_calls[0] == call(output_section.header)
  print_mock.mock_calls[1] == call(Message.DIR_SECTION_TITLE.value)
  print_mock.mock_calls[2] == call(Message.INVALID_DIR.value)
  print_mock.mock_calls[3] == call(f"{Message.OUT_DIR.value} {valid_dir}")
  print_mock.mock_calls[4] == call(output_section.footer)
  assert opts()['paths']['home'] == valid_dir
  assert opts()['outtmpl'] == None

@patch('builtins.input')
@patch('builtins.print')
def test_askOutputName(print_mock, input_mock):
  section = OutputSection('Test')

  input_mock.return_value = 'output_name.mp4'
  opts = section.run(askDir=False, askName=True, opts=Opts())

  print_mock.mock_calls[0] == call(section.header)
  print_mock.mock_calls[1] == call(Message.ENTER_NAME.value)
  print_mock.mock_calls[2] == call(section.footer)
  assert opts()['paths'] == {}
  assert opts()['outtmpl'] == 'output_name.mp4'

@patch('builtins.input', return_value='output_name.mp4')
@patch('tkinter.filedialog.askdirectory', return_value='/path/to/output/dir')
def test_not_change_param_opts(_, __):
  opts = Opts()
  backup_opts = opts.copy()
  OutputSection('').run(askDir=True, askName=True, opts=opts)
  assert opts == backup_opts