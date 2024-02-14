from sys import path
from pathlib import Path
path.append(Path('..').resolve().as_posix())

from unittest.mock import patch, Mock

from src.section.ListFormatSection import ListFormatSection
from src.structs.option import IOpt

class fake_opt (IOpt):
  def copy (self):
    return self
  def __init__(self) -> None:
    super().__init__()
    self.url = 'url'

@patch('src.section.ListFormatSection.YoutubeDL')
@patch('builtins.input')
def test(input_mock : Mock, youtubeDl_mock : Mock):
  # [(input value, expected do called)]
  case_ls : list[tuple[str, bool]] = [
    ('Y', True),
    ('N', False),
    ('', False)
  ]
  
  for case in case_ls:
    print('testing', case)
    input_val, excepted_do_called = case
    
    input_mock.reset_mock()
    youtubeDl_mock.reset_mock()
    
    input_mock.return_value = input_val
    ListFormatSection('').run(fake_opt())
    
    if excepted_do_called:
      assert youtubeDl_mock.called
      assert youtubeDl_mock.call_args.args[0]['listformats'] == True
    else:
      assert youtubeDl_mock.call_count == 0
