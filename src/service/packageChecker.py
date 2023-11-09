from importlib.metadata import version
import pip

def check():
  with open('requirements.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
      [name, ver] = line.split('==')
      try:
        # check if installed version is older than required version
        if version(name) >= ver:
          continue
      except:
        pass

      # package not installed or version not up to date
      print('installing', name, "==", ver)
      pip.main(['install', name + '==' + ver])

if __name__ == '__main__':
  check()