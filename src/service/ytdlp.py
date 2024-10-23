from collections import namedtuple
from contextlib import contextmanager
from contextlib import suppress
from http.cookiejar import MozillaCookieJar, LoadError
from http.cookiejar import MISSING_FILENAME_TEXT
from io import StringIO
from json import loads
from urllib.parse import quote as parse_quote, urlparse
from urllib.request import Request as UrlRequest
from re import match as re_match, sub as re_sub
from os import popen, fspath, environ as os_environ
from os import PathLike
from os import name as os_name
from os.path import expandvars as os_expandvars, expanduser as os_expanduser, join as join_path, dirname
from subprocess import run as run_cmd
from time import time
from typing import TypedDict, TypeVar, Union, Callable

from src.service.logger import Logger

from src.structs.option import IOpt

_T = TypeVar('_T')
_V = Union[_T, None]
EXE_NM = 'src\\yt-dlp.exe'

class _Params (TypedDict):
  cookiefile: _V[str]
  extract_flat: _V[bool]
  format: _V[str]
  outtmpl: _V[str]
  overwrites: _V[bool]
  paths: _V[dict[str, str]]
  quiet: _V[bool]
  skip_download: _V[bool]
  subtitleslangs: _V[list[str]]
  writeautomaticsub: _V[bool]
  writesubtitles: _V[bool]

class Ytdlp:
  @staticmethod
  def upgrade () -> None:
    run_cmd(f'{EXE_NM} -U')
  
  def __init__ (self, opt: IOpt = {}) -> None:
    self.params: _Params = opt.copy()
    self.base_cmd = self._build_base_cmd()
    self.logger = Logger()
      
  def _build_base_cmd (self) -> str:
    has_value : Callable[[str], bool] = lambda x : self.params.get(x, None) is not None
    is_true : Callable[[str], bool] = lambda x : self.params.get(x, False)
    
    return \
      f'{EXE_NM} ' + \
      (f'--cookies {self.params["cookiefile"]} '                 if has_value('cookiefile') else '') + \
      (f'--flat-playlist '                                       if is_true('extract_flat') else '') + \
      (f'--format {self.params["format"]} '                      if has_value('format') else '') + \
      (f'--force-overwrite '                                     if is_true('overwrites') else '') + \
      (f'-q '                                                    if is_true('quiet') else '') + \
      (f'--skip-download '                                       if is_true('skip_download') else '') + \
      (f'--write-sub '                                           if is_true('writesubtitles') else '') + \
      (f'--write-auto-sub '                                      if is_true('writeautomaticsub') else '') + \
      (f'--sub-lang {",".join(self.params["subtitleslangs"])} '  if has_value('subtitleslangs')else '') + \
      (f'-P {self.params["paths"]["home"]} '                     if has_value('paths') else '') + \
      (f'-o {self.params["outtmpl"]} '                           if has_value('outtmpl') else '')
      
  def extract_info (self, url: str) -> dict:
    # if no --list-subs, it cannot find some subtitles
    cmd = f'{self.base_cmd} -J --list-subs -q {url}'
    self.logger.debug(f"Running command: {cmd}")
    
    # since --list-subs is used, only the last line of the output is the metadata (\n is the last char)
    info = loads(popen(cmd).read().split('\n')[-2])
    json_name = self.logger.dump_dict(info)
    self.logger.debug(f'Metadata of {url} has been saved to {json_name}.json')

    return info
  
  def download (self, url: str) -> None:
    cmd = f'{self.base_cmd} {url}'
    self.logger.debug(f"Running command: {cmd}")
    run_cmd(cmd)
    
class YoutubeDLCookieJar(MozillaCookieJar):
  """
  This class is copied from yt_dlp module (version 2024.7.9)\n
  See [1] for cookie file format.
  1. https://curl.haxx.se/docs/http-cookies.html
  """
  
  _HTTPONLY_PREFIX = '#HttpOnly_'
  _ENTRY_LEN = 7
  _HEADER = '''# Netscape HTTP Cookie File
# This file is generated by yt-dlp.  Do not edit.
'''
  _CookieFileEntry = namedtuple(
    'CookieFileEntry',
    ('domain_name', 'include_subdomains', 'path', 'https_only', 'expires_at', 'name', 'value'))

  def __init__(self, filename=None, *args, **kwargs):
    if self.is_path_like(filename):
      filename = fspath(filename)
    super().__init__(filename, *args, **kwargs)    

  @staticmethod
  def _true_or_false(cndn):
    return 'TRUE' if cndn else 'FALSE'
    
  @staticmethod
  def is_path_like(f):
    return isinstance(f, (str, bytes, PathLike))
  
  @staticmethod
  def remove_dot_segments(path):
    # Implements RFC3986 5.2.4 remote_dot_segments
    # Pseudo-code: https://tools.ietf.org/html/rfc3986#section-5.2.4
    # https://github.com/urllib3/urllib3/blob/ba49f5c4e19e6bca6827282feb77a3c9f937e64b/src/urllib3/util/url.py#L263
    output = []
    segments = path.split('/')
    for s in segments:
      if s == '.':
        continue
      elif s == '..':
        if output:
          output.pop()
      else:
          output.append(s)
    if not segments[0] and (not output or output[0]):
      output.insert(0, '')
    if segments[-1] in ('.', '..'):
      output.append('')
    return '/'.join(output)

  @staticmethod 
  def escape_rfc3986(s):
    """Escape non-ASCII characters as suggested by RFC 3986"""
    return parse_quote(s, b"%/;:@&=+$,!~*'()?#[]")

  @staticmethod
  def normalize_url(url):
    """Normalize URL as suggested by RFC 3986"""
    escape_rfc3986 = YoutubeDLCookieJar.escape_rfc3986
    url_parsed = urlparse(url)
    return url_parsed._replace(
      netloc=url_parsed.netloc.encode('idna').decode('ascii'),
      path=escape_rfc3986(YoutubeDLCookieJar.remove_dot_segments(url_parsed.path)),
      params=escape_rfc3986(url_parsed.params),
      query=escape_rfc3986(url_parsed.query),
      fragment=escape_rfc3986(url_parsed.fragment),
    ).geturl()
    
  @staticmethod
  def sanitize_url(url, *, scheme='http'):
    # Prepend protocol-less URLs with `http:` scheme in order to mitigate
    # the number of unwanted failures due to missing protocol
    if url is None:
      return
    elif url.startswith('//'):
      return f'{scheme}:{url}'
    # Fix some common typos seen so far
    COMMON_TYPOS = (
      # https://github.com/ytdl-org/youtube-dl/issues/15649
      (r'^httpss://', r'https://'),
      # https://bx1.be/lives/direct-tv/
      (r'^rmtp([es]?)://', r'rtmp\1://'),
    )
    for mistake, fixup in COMMON_TYPOS:
      if re_match(mistake, url):
        return re_sub(mistake, fixup, url)
    return url
  
  @staticmethod
  def compat_expanduser(path):
    if os_name not in ('nt', 'ce'):
      return os_expanduser(path)

    HOME = os_environ.get('HOME')
    if not HOME:
        return os_expanduser(path)
    elif not path.startswith('~'):
        return path
    i = path.replace('\\', '/', 1).find('/')  # ~user
    if i < 0:
        i = len(path)
    userhome = join_path(dirname(HOME), path[1:i]) if i > 1 else HOME
    return userhome + path[i:]
  
  @staticmethod
  def expand_path(s):
    """Expand shell variables and ~"""
    return os_expandvars(YoutubeDLCookieJar.compat_expanduser(s))

  @contextmanager
  def open(self, file, *, write=False):
    if self.is_path_like(file):
      with open(file, 'w' if write else 'r', encoding='utf-8') as f:
        yield f
    else:
      if write:
        file.truncate(0)
      yield file

  def _really_save(self, f, ignore_discard, ignore_expires):
    now = time()
    for cookie in self:
      if (not ignore_discard and cookie.discard
          or not ignore_expires and cookie.is_expired(now)):
        continue
      name, value = cookie.name, cookie.value
      if value is None:
        # cookies.txt regards 'Set-Cookie: foo' as a cookie
        # with no name, whereas http.cookiejar regards it as a
        # cookie with no value.
        name, value = '', name
      f.write('{}\n'.format('\t'.join((
        cookie.domain,
        self._true_or_false(cookie.domain.startswith('.')),
        cookie.path,
        self._true_or_false(cookie.secure),
        '' if cookie.expires is None else str(cookie.expires),
        name, value,
      ))))

  def save(self, filename=None, ignore_discard=True, ignore_expires=True):
    """
    Save cookies to a file.
    Code is taken from CPython 3.6
    https://github.com/python/cpython/blob/8d999cbf4adea053be6dbb612b9844635c4dfb8e/Lib/http/cookiejar.py#L2091-L2117 """

    if filename is None:
      if self.filename is not None:
        filename = self.filename
      else:
        raise ValueError(MISSING_FILENAME_TEXT)

    # Store session cookies with `expires` set to 0 instead of an empty string
    for cookie in self:
      if cookie.expires is None:
        cookie.expires = 0

    with self.open(filename, write=True) as f:
      f.write(self._HEADER)
      self._really_save(f, ignore_discard, ignore_expires)

  def load(self, filename=None, ignore_discard=True, ignore_expires=True):
    """Load cookies from a file."""
    if filename is None:
      if self.filename is not None:
        filename = self.filename
      else:
        raise ValueError(MISSING_FILENAME_TEXT)

    def prepare_line(line):
      if line.startswith(self._HTTPONLY_PREFIX):
        line = line[len(self._HTTPONLY_PREFIX):]
      # comments and empty lines are fine
      if line.startswith('#') or not line.strip():
        return line
      cookie_list = line.split('\t')
      if len(cookie_list) != self._ENTRY_LEN:
        raise LoadError(f'invalid length {len(cookie_list)}')
      cookie = self._CookieFileEntry(*cookie_list)
      if cookie.expires_at and not cookie.expires_at.isdigit():
        raise LoadError(f'invalid expires at {cookie.expires_at}')
      return line

    cf = StringIO()
    with self.open(filename) as f:
      for line in f:
        try:
          cf.write(prepare_line(line))
        except LoadError as e:
          if f'{line.strip()} '[0] in '[{"':
            raise LoadError(
              'Cookies file must be Netscape formatted, not JSON. See  '
              'https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp')
          continue
    cf.seek(0)
    self._really_load(cf, filename, ignore_discard, ignore_expires)
    # Session cookies are denoted by either `expires` field set to
    # an empty string or 0. MozillaCookieJar only recognizes the former
    # (see [1]). So we need force the latter to be recognized as session
    # cookies on our own.
    # Session cookies may be important for cookies-based authentication,
    # e.g. usually, when user does not check 'Remember me' check box while
    # logging in on a site, some important cookies are stored as session
    # cookies so that not recognizing them will result in failed login.
    # 1. https://bugs.python.org/issue17164
    for cookie in self:
      # Treat `expires=0` cookies as session cookies
      if cookie.expires == 0:
        cookie.expires = None
        cookie.discard = True

  def get_cookie_header(self, url):
    """Generate a Cookie HTTP header for a given url"""
    cookie_req = UrlRequest(self.normalize_url(self.sanitize_url(url)))
    self.add_cookie_header(cookie_req)
    return cookie_req.get_header('Cookie')

  def get_cookies_for_url(self, url):
    """Generate a list of Cookie objects for a given url"""
    # Policy `_now` attribute must be set before calling `_cookies_for_request`
    # Ref: https://github.com/python/cpython/blob/3.7/Lib/http/cookiejar.py#L1360
    self._policy._now = self._now = int(time())
    return self._cookies_for_request(UrlRequest(self.normalize_url(self.sanitize_url(url))))

  def clear(self, *args, **kwargs):
    with suppress(KeyError):
      return super().clear(*args, **kwargs)
