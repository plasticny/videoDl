from unittest.mock import patch, call

from src.section.OutputSection import OutputSection, Message
from src.dlConfig import DefaultConfig

def test_all_not_ask():
  section = OutputSection('', askDir=False, askName=False)
  output_dir, output_name = section.run()
  assert output_dir == DefaultConfig.outputDir.value
  assert output_name == DefaultConfig.outputName.value

@patch('tkinter.filedialog.askdirectory')
@patch('builtins.print')
def test_askOutputDir(print_mock, askdirectory_mock):
  output_section = OutputSection('Test Output Section', askDir=True, askName=False)

  # First test with invalid directory, then with valid directory
  valid_dir = '/path/to/output/dir'
  askdirectory_mock.side_effect = ['', valid_dir]
  
  outputDir, _ = output_section.run()

  print_mock.mock_calls[0] == call(output_section.header)
  print_mock.mock_calls[1] == call(Message.DIR_SECTION_TITLE.value)
  print_mock.mock_calls[2] == call(Message.INVALID_DIR.value)
  print_mock.mock_calls[3] == call(f"{Message.OUT_DIR.value} {valid_dir}")
  print_mock.mock_calls[4] == call(output_section.footer)
  assert outputDir == valid_dir

@patch('builtins.input')
@patch('builtins.print')
def test_askOutputName(print_mock, input_mock):
  section = OutputSection('Test Output Section', askDir=False, askName=True)

  # Test with custom name
  input_mock.return_value = 'output_name.mp4'
  _, output_name = section.run()
  print_mock.mock_calls[0] == call(section.header)
  print_mock.mock_calls[1] == call(Message.ENTER_NAME.value)
  print_mock.mock_calls[2] == call(section.footer)
  assert output_name == 'output_name.mp4'

  # Test with default name
  input_mock.return_value = ''
  _, output_name = section.run()
  assert output_name == DefaultConfig.outputName.value
