from dlConfig import dlConfig

from section.UrlSection import UrlSection
from section.LoginSection import LoginSection
from section.ListSubtitleSection import ListSubtitleSection
from section.ListFormatSection import ListFormatSection
from section.SetUpDownloadSection import SetUpDownloadSection
from section.DownloadSection import DownloadSection
from section.H264Section import H264Section

# main process
def run ():
    print("----------------- Download -----------------", end='\n\n')

    while True:
        config = dlConfig()
                
        # ask url
        config.url = UrlSection(title='Url').run()
                        
        # ask Login
        config.cookieFile = LoginSection(title='Login').run()
     
        # list subtitle
        ListSubtitleSection(title='List Subtitle', config=config).run()

        # list format
        ListFormatSection(title='List Format', config=config).run()
        
        # ask download configs
        setupConfig = SetUpDownloadSection(
            title='Set up download', config=config,
            outputName=False, h264=False
        ).run()
        config.overwriteConfigBy(setupConfig)
                
        # config.autoSetFileName()
                
        # do download
        DownloadSection(title="Downloading", config=config).run()
        
        # convert to h264
        # if config.h264 == True:
        #     H264Section(title='Convert to h264', config=config).run()