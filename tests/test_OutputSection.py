from sys import path
path.append('src')

from unittest.mock import patch, call

from src.section.OutputSection import OutputSection, Message
from src.service.YtDlpHelper import Opts

def test_all_not_ask():
  opts_ls = OutputSection('').run(askDir=False, askName=False, opts_ls=[Opts()])
  assert len(opts_ls) == 1
  assert opts_ls[0].outputDir == None
  assert opts_ls[0].outputName == None

@patch('tkinter.filedialog.askdirectory')
@patch('builtins.print')
def test_askOutputDir(print_mock, askdirectory_mock):
  output_section = OutputSection('Test')

  # First test with invalid directory, then with valid directory
  valid_dir = '/path/to/output/dir'
  askdirectory_mock.side_effect = ['', valid_dir]
  
  opts_ls = output_section.run(askDir=True, askName=False, opts_ls=[Opts()])

  assert len(opts_ls) == 1
  assert opts_ls[0].outputDir == valid_dir
  assert opts_ls[0].outputName == None

@patch('builtins.input')
@patch('builtins.print')
def test_askOutputName(print_mock, input_mock):
  section = OutputSection('Test')

  input_mock.return_value = 'output_name.mp4'
  opts_ls = section.run(askDir=False, askName=True, opts_ls=[Opts()])

  assert len(opts_ls) == 1
  assert opts_ls[0].outputDir == None
  assert opts_ls[0].outputName == 'output_name.mp4'

@patch('builtins.input', return_value='output_name.mp4')
@patch('tkinter.filedialog.askdirectory', return_value='/path/to/output/dir')
def test_not_change_param_opts(_, __):
  opts_ls = [Opts()]
  backup_opts_ls = [opts.copy() for opts in opts_ls]
  OutputSection('').run(askDir=True, askName=True, opts_ls=opts_ls)
  assert len(opts_ls) == len(backup_opts_ls)
  for opts, backup_opts in zip(opts_ls, backup_opts_ls):
    print(opts.toParams())
    print(backup_opts.toParams())
    assert opts == backup_opts