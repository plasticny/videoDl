from importlib.metadata import version
from math import pow
import pip

def versionToInt(version: str) -> int:
  version = version.strip().split('.')
  version = [pow(2, len(version)-idx-1)*int(v) for idx, v in enumerate(version)]
  return int(sum(version))

def versionFullfill(v1:str, v2:str) -> bool:
  """Check if v1 is newer than v2"""
  return versionToInt(v1) >= versionToInt(v2)

def check():
  with open('requirements.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
      [name, ver] = line.split('==')

      isFullfill = False
      try:
        # check if installed version is older than required version
        isFullfill = versionFullfill(version(name), ver)
      except:
        pass

      # package not installed or version not up to date
      if not(isFullfill):
        print('installing', name, "==", ver)
        pip.main(['install', name + '==' + ver])

if __name__ == '__main__':
  check()