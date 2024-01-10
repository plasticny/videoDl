from unittest.mock import patch

from src.section.OutputSection import OutputSection

def test_all_not_ask():
  ret = OutputSection().run(askDir=False, askName=False)
  assert ret['dir'] == None
  assert ret['name'] == None

@patch('tkinter.filedialog.askdirectory')
def test_ask_dir(askdirectory_mock):
  output_section = OutputSection('Test')

  # First test with invalid directory, then with valid directory
  valid_dir = '/path/to/output/dir'
  askdirectory_mock.side_effect = ['', valid_dir]
  
  ret = output_section.run(askDir=True, askName=False)
  assert ret['dir'] == valid_dir
  assert ret['name'] == None

@patch('builtins.input')
def test_ask_name(input_mock):
  section = OutputSection('Test')

  input_mock.return_value = 'output_name.mp4'
  ret = section.run(askDir=False, askName=True)
  assert ret['dir'] == None
  assert ret['name'] == 'output_name.mp4'