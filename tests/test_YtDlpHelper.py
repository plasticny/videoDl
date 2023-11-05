from src.service.YtDlpHelper import Opts

def test_opts_eq():
  opts = Opts()

  # test same
  assert opts == opts

  # test different
  for key in opts():
    other_opts = opts.copy()
    if key == 'paths':
      other_opts.outputDir({'a': 1, 'b': 2})
    elif key == 'subtitleslangs':
      other_opts.subtitlesLang(['a', 'b'])
    else:
      other_opts.opts[key] = 'other'
    assert opts != other_opts