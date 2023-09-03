from subprocess import call

YT_EXE_FILE = 'yt-dlp.exe'

# paramCommands: list of params command
def runCommand (execCommand=YT_EXE_FILE, paramCommands:list=[], printCommand:bool=False):
    command = execCommand
    for param in paramCommands:
        if len(param) == 0:
            continue
        command = f'{command} {param}'

    if printCommand:
        print("## Executed Command ##")
        print(command, end='\n\n')

    call(command, shell=True)
