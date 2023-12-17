from service.fetcher import BiliBiliFetcher
from section.LoginSection import LoginSection
from section.UrlSection import UrlSection
from section.OutputSection import OutputSection
import requests
from tqdm import tqdm

url = UrlSection('Url').run()
opts = LoginSection('Login').run()
opts = OutputSection('Output').run([opts], askName=False)[0]

bvid = url[-13:-1]
aid = BiliBiliFetcher.bvid_2_aid(bvid)
cids = BiliBiliFetcher.get_page_cids(bvid)
for idx, cid in enumerate(cids):
  qns = BiliBiliFetcher.get_accept_quality(aid, cid, opts)
  best_quality = qns[0]['quality']

  video_url = BiliBiliFetcher.get_playurl(aid, cid, best_quality, opts)

  # download video
  header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
  }
  res = requests.Session().get(video_url, headers=header, stream=True)

  print(f'Downloading video {idx+1}/{len(cids)}...')
  with open(f'{opts.outputDir}\\video{idx+1}.mp4', 'wb') as f:
    total_length = int(res.headers.get('content-length'))
    with tqdm(total=total_length, unit='B', unit_scale=True) as pbar:
      for chunk in res.iter_content(chunk_size=1024):
        f.write(chunk)
        pbar.update(len(chunk))