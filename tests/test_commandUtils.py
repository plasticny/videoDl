from unittest.mock import patch, call

from src.service.commandUtils import runCommand

@patch('builtins.print')
def test(print_mock):
  result = runCommand(
    execCommand='echo',
    paramCommands=['Hello', 'World', ''], # '' is for test handling empty param
    printCommand=True,
    catch_stdout=True
  )

  assert print_mock.call_count == 2
  assert print_mock.mock_calls[0] == call('## Executed Command ##')
  assert print_mock.mock_calls[1] == call('echo Hello World', end='\n\n')
  assert result.returncode == 0
  assert result.stdout.decode('utf-8').startswith('Hello World')

def test_noPrint(capfd):
  result = runCommand(
    execCommand='echo',
    paramCommands=['Hello', 'World']
  )
  out, err = capfd.readouterr()
  assert out == 'Hello World\r\n'
  assert err == ''
  assert result.returncode == 0
  assert result.stdout == None

def test_error():
  result = runCommand(
    execCommand='notExistCommand',
    paramCommands=[],
    printCommand=False
  )
  assert result.returncode != 0
  assert result.stdout == None