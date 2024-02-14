from unittest.mock import patch, Mock

from src.section.OutputSection import OutputSection

def test_all_not_ask():
  ret = OutputSection().run(askDir=False, askName=False)
  assert ret['dir'] == None
  assert ret['name'] == None

@patch('src.section.OutputSection.get_output_dir_autofill')
@patch('tkinter.filedialog.askdirectory')
def test_ask_dir(askdirectory_mock:Mock, autofill_mock:Mock):
  fake_dir = '/path/to/output/dir'
  
  # test cases [(autofill, fake input, expected return dir)]
  case_ls : list[tuple[str, list[str], str]] = [
    # no autofill, first input is invalid, second input is valid
    (None, ['', fake_dir], fake_dir),
    # autofill
    (fake_dir, [], fake_dir)
  ]
  
  for case in case_ls:
    print('testing', case)
    case_autofill, case_input, expected_dir = case
    
    autofill_mock.reset_mock()
    askdirectory_mock.reset_mock()
    
    autofill_mock.return_value = case_autofill
    askdirectory_mock.side_effect = case_input
    
    ret = OutputSection().run(askName=False)
    assert ret['dir'] == expected_dir
    assert ret['name'] == None
    
    if case_autofill:
      assert not askdirectory_mock.called

@patch('builtins.input')
def test_ask_name(input_mock):
  section = OutputSection('Test')

  input_mock.return_value = 'output_name.mp4'
  ret = section.run(askDir=False, askName=True)
  assert ret['dir'] == None
  assert ret['name'] == 'output_name.mp4'