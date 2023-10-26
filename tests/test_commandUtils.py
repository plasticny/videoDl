from src.service.commandUtils import runCommand

def test(capfd):
  retc = runCommand(
    execCommand='echo',
    paramCommands=['Hello', 'World', ''], # '' is for test handling empty param
    printCommand=True
  )
  out, err = capfd.readouterr()
  assert out == '## Executed Command ##\necho Hello World\n\nHello World\r\n'
  assert err == ''
  assert retc == 0

def test_noPrint(capfd):
  retc = runCommand(
    execCommand='echo',
    paramCommands=['Hello', 'World'],
    printCommand=False
  )
  out, err = capfd.readouterr()
  assert out == 'Hello World\r\n'
  assert err == ''
  assert retc == 0

def test_error():
  retc = runCommand(
    execCommand='notExistCommand',
    paramCommands=[],
    printCommand=False
  )
  assert retc != 0