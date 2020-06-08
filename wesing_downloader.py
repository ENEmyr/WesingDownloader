import requests, random, json
from os import mkdir
from bs4 import BeautifulSoup
from itertools import cycle
from optparse import OptionParser
from os.path import join, abspath, exists

def random_header():
    HEADERS_LIST = [
                'Mozilla/5.0 (Windows; U; Windows NT 6.1; x64; fr; rv:1.9.2.13) Gecko/20101203 Firebird/3.6.13',
                'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
                'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
                'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
                'Mozilla/5.0 (Windows NT 5.2; RW; rv:7.0a1) Gecko/20091211 SeaMonkey/9.23a1pre'
            ]
    return {'User-Agent': random.choice(HEADERS_LIST)} 

def get_proxies():
    proxy_url = 'https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all'
    res = requests.get(proxy_url, allow_redirects=True, headers=random_header())
    list_proxies = res.text.split('\n')
    list_proxies = list(filter(lambda x: x != '', list_proxies))
    list_proxies = list(map(lambda x: x.replace('\t', ''), list_proxies))
    return list_proxies    

def download_albums(urls:list):
    proxy_pool = cycle(get_proxies())
    if type(urls) != list:
        raise ValueError("urls muse be list")
    for url in urls:
        res = requests.get(url, headers=random_header(), proxies={"http": next(proxy_pool)})
        soup = BeautifulSoup(res.content, 'html.parser')
        elements = soup.findAll('a', {'class': 'mod_song_list__body'})
        alblum_name = soup.title.get_text()
        print(f'Starting download album {alblum_name}.')
        mkdir(f'downloaded/{alblum_name}')
        print('Album directory was created.')
        for e in elements:
            song_url = e['href']
            page = requests.get(song_url, headers=random_header(), proxies={"http": next(proxy_pool)})
            script_page = BeautifulSoup(page.content, 'html.parser')
            song_title = str(script_page.title.get_text())
            song_title = song_title[:song_title.rfind('-')]
            script = str(script_page.findAll('script')[3])
            start_index = script.find('playurl') + 10
            script = script[start_index:]
            stop_index = script.find('"')
            script = script[:stop_index]
            song_data = requests.get(script, allow_redirects=True, headers=random_header())
            save_path = join(abspath('.'), abspath(f'downloaded/{alblum_name}'), f'{song_title}.mp4')
            print(save_path)
            open(save_path, 'wb').write(song_data.content)
            print(f'{song_title}.mp4 has been downloaded.')

def download_tracks(uid:str, n_download:int = 1):
    proxy_pool = cycle(get_proxies())
    title_track_pairs = []
    print(f'Fetching tracks of user : {uid}')
    for i in range(1, n_download//8):
        url = f'https://cgi.wesingapp.com/fcgi-bin/kg_ugc_get_homepage?jsonpCallback=callback_1&g_tk=5381&outCharset=utf-8&format=jsonp&type=get_ugc&start={i}&num=8&touin=&share_uid={uid}&g_tk_openkey=5381&_=1591298074777'
        res = requests.get(url, headers=random_header(), proxies={"http": next(proxy_pool)})
        start_idx = res.text.find('[')
        stop_idx = res.text.rfind(']')+1
        json_str = '{ "tracks":' + res.text[start_idx:stop_idx] + '}'
        try:
            loaded_json = json.loads(json_str)
        except:
            print(json_str)
        loaded_json = json.loads(json_str)
        for track in loaded_json["tracks"]:
            track_url = f'https://wesingapp.com/play?s={track["shareid"]}'
            track_title = f'{track["title"]}.mp4'
            title_track_pairs.append((track_title, track_url))
    print('Track urls has been fetched')
    print('Starting download')
    for title, url in title_track_pairs:
        page = requests.get(url, headers=random_header(), proxies={"http": next(proxy_pool)})
        script_page = BeautifulSoup(page.content, 'html.parser')
        if script_page.findAll('script') == []:
            continue
        script = str(script_page.findAll('script')[3])
        start_index = script.find('playurl') + 10
        script = script[start_index:]
        stop_index = script.find('"')
        script = script[:stop_index]
        song_data = requests.get(script, allow_redirects=True, headers=random_header())
        save_path = join(abspath('.'), abspath(f'downloaded/{title}'))
        open(save_path, 'wb').write(song_data.content)
        print(f'{title} has been downloaded.')

parser = OptionParser()
parser.add_option('-a', '--album', dest='album', help="Relative path to album urls", default='')
parser.add_option('-t', '--track', dest='track', help="Uid of owner of tracks", default='')
parser.add_option('-n', '--n_tracks', dest='n_track', help="Number of tracks to download", default=1)

(options, args) = parser.parse_args()

if options.album == '' and options.track == '':
    raise Exception("Please specify arguments")

if not exists(join(abspath('.'), abspath('downloaded'))):
    mkdir('downloaded')
if options.album != '':
    urls = open(join(abspath('.'), abspath(options.album)), 'r').readlines()
    urls = list(map(lambda x: x.replace('\n', ''), urls))
    download_albums(urls)
if options.track != '':
    download_tracks(options.track, int(options.n_track))

print('Download completed.')