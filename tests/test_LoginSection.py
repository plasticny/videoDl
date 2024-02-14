from unittest.mock import patch

from src.section.LoginSection import LoginSection

def test():
  # [(autofill, input, filedialog, expected)]
  case_ls : list[tuple[str, str, str, str]] = [
    # not login
    (None, 'N', None, None),
    # login
    (None, 'Y', 'cookie.txt', 'cookie.txt'),
    # login canceled
    (None, 'Y', '', None),
    # autofill
    ('cookie.txt', None, None, 'cookie.txt')
  ]

  for case in case_ls:
    print('testing', case)
    case_autofill, case_input, case_filedialog, case_expected = case
    
    with\
      patch('src.section.LoginSection.get_login_autofill', return_value=case_autofill),\
      patch('builtins.input', return_value=case_input) as input_mock,\
      patch('tkinter.filedialog.askopenfilename', return_value=case_filedialog) as filedialog_mock\
    :
      assert LoginSection().run('url') == case_expected
      
      if case_autofill is not None:
        assert not input_mock.called
        assert not filedialog_mock.called
