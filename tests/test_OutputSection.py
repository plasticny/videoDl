from unittest.mock import patch, Mock

from src.section.OutputSection import OutputSection

def test_all_not_ask():
  ret = OutputSection().run(askDir=False, askName=False)
  assert ret['dir'] == None
  assert ret['name'] == None

@patch('src.section.OutputSection.get_output_dir_autofill')
@patch('tkinter.filedialog.askdirectory')
def test_ask_dir(askdirectory_mock:Mock, autofill_mock:Mock):
  output_section = OutputSection()

  # First test with invalid directory, then with valid directory
  valid_dir = '/path/to/output/dir'
  autofill_mock.return_value = None
  askdirectory_mock.side_effect = ['', valid_dir]
  
  ret = output_section.run(askName=False)
  assert ret['dir'] == valid_dir
  assert ret['name'] == None
  
  # autofill
  autofill_mock.return_value = valid_dir
  askdirectory_mock.reset_mock()
  ret = output_section.run(askName=False)
  assert ret['dir'] == valid_dir
  assert ret['name'] == None
  askdirectory_mock.assert_not_called()

@patch('builtins.input')
def test_ask_name(input_mock):
  section = OutputSection('Test')

  input_mock.return_value = 'output_name.mp4'
  ret = section.run(askDir=False, askName=True)
  assert ret['dir'] == None
  assert ret['name'] == 'output_name.mp4'