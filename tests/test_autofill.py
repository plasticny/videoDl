import src.service.autofill as autofill
from src.service.autofill import *

from unittest.mock import patch

def test_get_login_autofill ():
  fake_config = {
    'login': {
      'enable': False,
      'cookie_path': {
        'a': 'value',
        'b': ''
      }
    }
  }
  
  # test not enable
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_login_autofill('url') is None

  # test enable
  fake_config['login']['enable'] = True
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    # test key found
    assert get_login_autofill('url a') == 'value'  
    # test key found but value is empty
    assert get_login_autofill('url b') is None
    # test key not found
    assert get_login_autofill('url c') is None
    
def test_get_lyd_format_autofill ():  
  fake_config = {
    'format': {
      'enable': False,
      'prefered_format': 0
    }
  }
  
  # test not enable
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_lyd_format_autofill() is None

  # test enable
  fake_config['format']['enable'] = True
  # test prefered_format is 0
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_lyd_format_autofill() == 0
  # test prefered_format is 1
  fake_config['format']['prefered_format'] = 1
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_lyd_format_autofill() == 1
  # test prefered_format is not 0 or 1
  fake_config['format']['prefered_format'] = 2
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_lyd_format_autofill() is None
    
def test_get_do_write_subtitle_autofill ():
  fake_config = {
    'subtitle': {
      'do_write_subtitle': {
        'enable': False,
        'val': False
      }
    }
  }
  
  # test not enable
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_do_write_subtitle_autofill() is None

  # test enable
  fake_config['subtitle']['do_write_subtitle']['enable'] = True
  # test val is False
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_do_write_subtitle_autofill() == False

def test_get_sub_lang_autofill ():
  fake_config = {
    'subtitle': {
      'sub_lang': {
        'enable': False,
        'val': ['a', 'b']
      }
    }
  }
  
  # test not enable
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_sub_lang_autofill() is None

  # test enable
  fake_config['subtitle']['sub_lang']['enable'] = True
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_sub_lang_autofill() == ['a', 'b']
    
def test_get_sub_write_mode_autofill ():
  fake_config = {
    'subtitle': {
      'write_mode': {
        'enable': False,
        'embed': True,
        'burn': False
      }
    }
  }
  
  # test not enable
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_sub_write_mode_autofill() is None

  # test enable
  fake_config['subtitle']['write_mode']['enable'] = True
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_sub_write_mode_autofill() == (True, False)
    
def test_get_output_dir_autofill ():
  fake_config = {
    'download': {
      'output_dir': {
        'enable': False,
        'val': ''
      }
    }
  }
  
  # test not enable
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_output_dir_autofill() is None

  # === test enable === #
  # test val is empty
  fake_config['download']['output_dir']['enable'] = True
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_output_dir_autofill() is None
  # test val is not empty
  fake_config['download']['output_dir']['val'] = 'value'
  with patch.object(autofill, 'lyd_autofill_config', fake_config):
    assert get_output_dir_autofill() == 'value'

def test_all_disabled ():
  """ Check if all autofill is disabled before upload to git """
  assert get_login_autofill('url') is None
  assert get_lyd_format_autofill() is None
  assert get_do_write_subtitle_autofill() is None
  assert get_sub_lang_autofill() is None
  assert get_sub_write_mode_autofill() is None
  assert get_output_dir_autofill() is None
