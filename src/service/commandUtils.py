from enum import Enum

from subprocess import run, CompletedProcess, PIPE

YT_EXEC = 'yt-dlp.exe'
FFMPEG_EXEC = 'ffmpeg.exe'

class Message (Enum):
    EXECUTED_COMMAND = "## Executed Command ##"

# paramCommands: list of params command
# RETURN: exit code of command
def runCommand (execCommand, paramCommands:list=[], printCommand:bool=False, catch_stdout:bool=False) -> CompletedProcess:
    command = execCommand
    for param in paramCommands:
        if len(param) == 0:
            continue
        command = f'{command} {param}'

    if printCommand:
        print(Message.EXECUTED_COMMAND.value)
        print(command, end='\n\n')

    return run(command, shell=True, stdout=PIPE if catch_stdout else None)