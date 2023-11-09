from src.service.YtDlpHelper import Opts

def test_opts_eq():
  opts = Opts()
  opts.subtitlesLang(['a'])

  # test same
  assert opts == opts

  # test different
  for key in opts():
    other_opts = opts.copy()
    if key == 'subtitleslangs':
      other_opts.subtitlesLang(['a', 'b'])
    if key == 'postprocessors':
      other_opts.embedSubtitle(True)
    else:
      other_opts.opts[key] = 'other'
    assert opts != other_opts

def test_embedSubtitle():
  opts = Opts()

  opts.embedSubtitle(True)
  assert opts.opts['postprocessors'].count({'key': 'FFmpegEmbedSubtitle'}) == 1

  opts.opts['postprocessors'].append({'key': 'other'})
  opts.embedSubtitle(False)
  assert opts.opts['postprocessors'] == [{'key': 'other'}]