from dlConfig import dlConfig

from section.UrlSection import UrlSection
from section.LoginSection import LoginSection
from section.ListSubtitleSection import ListSubtitleSection
from section.ListFormatSection import ListFormatSection
from section.SetUpDownloadSection import SetUpDownloadSection
from section.DownloadSection import DownloadSection

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
        setupConfig = SetUpDownloadSection(title='Set up download').run()
        config.overwriteConfigBy(setupConfig)
        
        # do download
        DownloadSection(title="Downloading", config=config).run() 
