from requests import get
from importlib.metadata import version
from pip import main as pip
from colorama import Fore, Style
from os import environ

def check_update():
  if 'RUNTIME_ENV' in environ and environ['RUNTIME_ENV'] == 'prod':
    return
  
  print(f'{Fore.CYAN}Checking for updates...{Style.RESET_ALL}')
  releases : dict = get('https://pypi.org/pypi/yt_dlp/json').json()['releases']
  versions = list(releases.keys())

  latest = None
  for i in range(len(versions)-1, -1, -1):
    if 'dev' not in versions[i]:
      latest = versions[i]
      break

  if latest != version('yt_dlp'):
    print('Updating...')
    pip(['install', '--upgrade', 'yt-dlp'])

  print()
