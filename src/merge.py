import subprocess
import tkinter.filedialog as tkFileDialog
from os import rename

def getInputFile(title, filetypes):
    filePath = tkFileDialog.askopenfilename(title=title, filetypes=filetypes)
    # replace space in the filePath
    filePath_replace = filePath.replace(' ', '_').replace('&','_')
    if filePath != filePath_replace:
        rename(filePath, filePath_replace)
    return filePath_replace
    
while True:
    # select video
    print('Select video file:')
    video = getInputFile(title='video', 
                         filetypes=[
                            ('Mp4 file', '*.mp4'),
                            ('All file', '*.*')
                        ])
    print('video file name:', video, end='\n\n')

    # select audio
    print('Select audio file:')
    audio = getInputFile(title='audio',
                         filetypes=[
                            ('Audio file', ('*.wav', '*.m4a')),
                            ('All file', '*.*')
                        ])
    print('audio file name:', audio, end='\n\n')

    # select output
    print('Select output location and filename:')
    output = tkFileDialog.asksaveasfilename(initialfile='output', title='output', filetypes=[('Mp4 file', '*.mp4')])
    if output[-4:] != '.mp4':
        output += '.mp4'
    # replace all space with '_'
    output = output.replace(' ', '_').replace('&','_')
    print('Output file path:', output, end='\n\n')

    # perform merging
    print("Merging...")
    outputlib264 = input('output as libx264 format? (N)').upper()
    if outputlib264 == 'N' or outputlib264 == '':
        cmd_command = f"ffmpeg -i {video} -i {audio} -c:v copy -c:a aac {output}"
    else:
        cmd_command = f"ffmpeg -i {video} -i {audio} -c:v libx264 -c:a aac {output}"
    subprocess.call(cmd_command, shell=True)
    print("done", end="\n\n")
    
    contin = input('continue?(N) ').upper()
    if contin == 'N' or contin == '':
        break