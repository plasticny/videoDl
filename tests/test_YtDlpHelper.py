from sys import path
path.append('src')

from src.service.YtDlpHelper import Opts
from src.service.structs import Subtitle

def test_opts_eq():
  opts = Opts()
  opts.setSubtitle(Subtitle('a', 'a', False))

  # test same
  assert opts == opts

  # test different
  for key in opts.toParams():
    other_opts = opts.copy()
    if key == 'postprocessors':
      other_opts.embedSubtitle = True
    else:
      other_opts.opts[key] = 'other'
    assert opts != other_opts

def test_toParams():
  opts = Opts()
  optsc = opts.copy()

  for key in opts.toParams().keys():
    if key == 'not_yt_dlp':
      assert key not in optsc.opts
    else:
      assert key in optsc.opts