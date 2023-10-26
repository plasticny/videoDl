from subprocess import call

YT_EXEC = 'yt-dlp.exe'
FFMPEG_EXEC = 'ffmpeg.exe'

# paramCommands: list of params command
# RETURN: exit code of command
def runCommand (execCommand, paramCommands:list=[], printCommand:bool=False) -> int:
    command = execCommand
    for param in paramCommands:
        if len(param) == 0:
            continue
        command = f'{command} {param}'

    if printCommand:
        print("## Executed Command ##")
        print(command, end='\n\n')

    return call(command, shell=True)