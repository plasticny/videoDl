import src.service.autofill as autofill
from src.service.autofill import *

from unittest.mock import patch

def test_get_login_autofill ():
  # [(do_enable, url, autofill_value)]
  case_ls : list[tuple[bool, str, str]] = [
    # when not enable
    (False, 'url', None),
    # when enable and key found
    (True, 'url a', 'value'),
    # when enable and key found but value is empty
    (True, 'url b', None),
    # when enable and key not found
    (True, 'url c', None)
  ]
  fake_config = {
    'login': {
      'enable': False,
      'cookie_path': {
        'a': 'value',
        'b': ''
      }
    }
  }
  
  for case in case_ls:
    print('testing', case)
    do_enable, url, autofill_value = case
    fake_config['login']['enable'] = do_enable
    with patch.object(autofill, 'lyd_autofill_config', fake_config):
      assert get_login_autofill(url) == autofill_value
    
def test_get_lyd_format_autofill ():
  # [(do_enable, prefered_format, autofill_value)]
  case_ls : list[tuple[bool, int, int]] = [
    # when not enable
    (False, 0, None),
    # when enable and prefered format is available
    (True, 0, 0),
    (True, 1, 1),
    (True, 2, 2),
    # when the prefered format is not available
    (True, 3, None)
  ]
  fake_config = {
    'format': {
      'enable': False,
      'prefered_format': 0
    }
  }
  
  for case in case_ls:
    print('testing', case)
    do_enable, prefered_format, autofill_value = case
    fake_config['format']['enable'] = do_enable
    fake_config['format']['prefered_format'] = prefered_format
    with patch.object(autofill, 'lyd_autofill_config', fake_config):
      assert get_lyd_format_autofill() == autofill_value
    
def test_get_do_write_subtitle_autofill ():
  # [(do_enable, val, autofill_value)]
  case_ls : list[tuple[bool, bool, bool]] = [
    # when not enable
    (False, True, None),
    # when enable and val is False
    (True, False, False),
    # when enable and val is True
    (True, True, True)
  ]
  fake_config = {
    'subtitle': {
      'do_write_subtitle': {
        'enable': False,
        'val': False
      }
    }
  }
  
  for case in case_ls:
    print('testing', case)
    do_enable, val, autofill_value = case
    fake_config['subtitle']['do_write_subtitle']['enable'] = do_enable
    fake_config['subtitle']['do_write_subtitle']['val'] = val
    with patch.object(autofill, 'lyd_autofill_config', fake_config):
      assert get_do_write_subtitle_autofill() == autofill_value

def test_get_sub_lang_autofill ():
  # [(do_enable, val, autofill_value)]
  case_ls : list[tuple[bool, list[str], list[str]]] = [
    # when not enable
    (False, ['a', 'b'], None),
    # when enable 1
    (True, ['a', 'b'], ['a', 'b']),
    # when enable 2
    (True, ['c'], ['c'])
  ]
  fake_config = {
    'subtitle': {
      'sub_lang': {
        'enable': False,
        'val': ['a', 'b']
      }
    }
  }
  
  for case in case_ls:
    print('testing', case)
    do_enable, val, autofill_value = case
    fake_config['subtitle']['sub_lang']['enable'] = do_enable
    fake_config['subtitle']['sub_lang']['val'] = val
    with patch.object(autofill, 'lyd_autofill_config', fake_config):
      assert get_sub_lang_autofill() == autofill_value
    
def test_get_sub_write_mode_autofill ():
  # [(do_enable, embed, burn, autofill_value)]
  case_ls : list[tuple[bool, bool, bool, tuple[bool, bool]]] = [
    # when not enable
    (False, True, False, None),
    # when enable and only embed
    (True, True, False, (True, False)),
    # when enable and only burn
    (True, False, True, (False, True)),
    # when enable and both
    (True, True, True, (True, True))
  ] 
  fake_config = {
    'subtitle': {
      'write_mode': {
        'enable': False,
        'embed': True,
        'burn': False
      }
    }
  }
  
  for case in case_ls:
    print('testing', case)
    do_enable, embed, burn, autofill_value = case
    fake_config['subtitle']['write_mode']['enable'] = do_enable
    fake_config['subtitle']['write_mode']['embed'] = embed
    fake_config['subtitle']['write_mode']['burn'] = burn
    with patch.object(autofill, 'lyd_autofill_config', fake_config):
      assert get_sub_write_mode_autofill() == autofill_value
    
def test_get_output_dir_autofill ():
  # [(do_enable, val, autofill_value)]
  case_ls : list[tuple[bool, str, str]] = [
    # when not enable
    (False, 'a', None),
    # when enable but val is empty
    (True, '', None),
    # when enable and val is not empty 1
    (True, 'b', 'b'),
    # when enable and val is not empty 2
    (True, 'ce', 'ce')
  ]
  fake_config = {
    'download': {
      'output_dir': {
        'enable': False,
        'val': ''
      }
    }
  }
  
  for case in case_ls:
    print('testing', case)
    do_enable, val, autofill_value = case
    fake_config['download']['output_dir']['enable'] = do_enable
    fake_config['download']['output_dir']['val'] = val
    with patch.object(autofill, 'lyd_autofill_config', fake_config):
      assert get_output_dir_autofill() == autofill_value

def test_all_disabled ():
  """ Check if all autofill is disabled before upload to git """
  assert get_login_autofill('url') is None
  assert get_lyd_format_autofill() is None
  assert get_do_write_subtitle_autofill() is None
  assert get_sub_lang_autofill() is None
  assert get_sub_write_mode_autofill() is None
  assert get_output_dir_autofill() is None
