# VideoDl
<p>
  Cli video download tool base on yt-dlp. (This tool attempts to provide a cli for yt-dlp)
</p>
<p>
  - python 3.11.5</br>
  - pytest</br>
  - yt-dlp (https://github.com/yt-dlp/yt-dlp)</br>
  - ffmpeg
</p>
<p>
  Only tested in window 10 system.
</p>

## Features
There are two tools in this project.

### lyd.bat (lazy youtube download)
This tool tries to minimize the setting during download video<br/>
<ul>
  <li>Enter url to download</li>
  <li>Download best quality automatically</li>
  <li>Select subtitle if any and hard-burn/soft-embed into the video</li>
  <li>Login with cookie file if the site requires to login. See readme.md in cookie folder for more instructions.</li>
  <li>Download playlist if the url links to a playlist</li>
  <li>Pre-set downlaod settings with a toml file (the file in /src/lyd_autofill.toml)</li>
</ul>
Execute lyd.bat to run this tool.

### download.bat
This tool provide interface of basic setting when using ytp-dlp to downlaod video.<br/>
Execute download.bat to run this tool.</br>
<b>However, this tool current not work well and is used as a debug helper. So use lyd instead.</b>

## Tested sites
This tool is tested to be able to download video from these sites:
<ul>
  <li>Youtube</li>
  <li>Bilibili</li>
  <li>Instagram</li>
  <li>Facebook</li>
  <li>Pinterest</li>
</ul>

## Testing
Install modules in requirements.txt and test-requirements.txt.<br>
In project root, execute
```
pytest
```

## Compile lyd
Install modules in requirements.txt and compile-requirements.txt.<br>
In project root, execute
```
pyinstaller lazyYtDownload.spec
```
<p>
  The exe file will be generated in /dist/lazyYtDownload
</p>
<i>Note: pyinstaller generate build and dist folder. Delete these folders for a clean compilation</i>

## About the release
Only lazyYtDownload had release its compiled exe file
<ul>
  <li>execute lazyYtDownload.exe to run the tool</li>
  <li>The lyd_autofill.toml for pre-setup download setting is stored in /_internal</li>
</ul>

## Note for developing
<ul>
  <li>
    The extract_info function of yt_dlp doest not work well when getting info of bilibili video, so those info is extract with a custom fetcher.
  </li>
</ul>
