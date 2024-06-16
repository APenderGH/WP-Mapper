import requests
import sys
import argparse
import json
from termcolor import colored

API_URI = '/wp-json/wp/v2'
MEDIA_URI = '/media'
COLLECTION_URIS = {
    'comments':'/comments',
    'media':'/media',
    'pages':'/pages',
    'posts':'/posts',
    'users':'/users'
}
COLLECTION_NAMES = []
for name,uri in COLLECTION_URIS.items():
    COLLECTION_NAMES.append(name)

def list_of_strings(arg):
    return arg.split(',')

parser = argparse.ArgumentParser(prog="WPMapper", description="Find the weird stuff quickly. Lists attachments, posts, pages, etc of a WordPress site.")
parser.add_argument("target", help="The URL of the target site: http(s)://<xxx>/")
parser.add_argument("-x", dest="proxy", help="Proxy URL to pass requests through.")
parser.add_argument("-c", dest="collecting", type=list_of_strings, help=f"Comma separated list of things to collect, default is everything. Options are: {COLLECTION_NAMES}", default=COLLECTION_NAMES)
args = parser.parse_args()

PROXIES = {"http":args.proxy,"https":args.proxy} if (args.proxy != None) else {}

def api_get_all(collection_uri):
    base_url = args.target + API_URI + collection_uri + "?per_page=100"
    total_pages = int(requests.get(base_url, proxies=PROXIES, verify=False).headers["X-WP-TotalPages"])
    string_data = ""
    for page in range(1, total_pages+1):
        r = requests.get(base_url + f"&page={page}", proxies=PROXIES, verify=False)
        if page != total_pages:
            string_data = string_data + r.content.decode(encoding='utf-8') + ','
        else:
            string_data = string_data + r.content.decode(encoding='utf-8')
    return json.loads('[' + string_data + ']')

def check_connection(url):
    try:
        requests.get(url, verify=False)
        return True
    except:
        return False
        

def collect_media(url):
    for group in api_get_all(COLLECTION_URIS['media']):
        for media in group:
            print(media['source_url'])        
    return

def collect_pages(url):
    for group in api_get_all(COLLECTION_URIS['pages']):
        for media in group:
            print(media['link'])        
    return

def collect_posts(url):
    for group in api_get_all(COLLECTION_URIS['posts']):
        for media in group:
            print(media['link'])        
    return

def collect_users(url):
    for group in api_get_all(COLLECTION_URIS['users']):
        for media in group:
            print(media['link'])        
    return

def collect_comments(url):
    for group in api_get_all(COLLECTION_URIS['comments']):
        for media in group:
            print(media['link'])
            print(media['content'])        
    return

if __name__ == '__main__':
    assert check_connection(args.target), colored("Could not connect to target.", "red", attrs=["bold"])
    print(f"Target Connection: " + colored(f"OK", "green", attrs=["bold"]))
    print(colored("Starting Collection", "white", attrs=["bold"]))
    
    if 'media' in args.collecting:
        print(colored("--- Media ---", "yellow", attrs=["bold"]))
        collect_media(args.target)
    
    if 'pages' in args.collecting:
        print(colored("--- Pages ---", "yellow", attrs=["bold"]))
        collect_pages(args.target)
    
    if 'posts' in args.collecting:
        print(colored("--- Posts ---", "yellow", attrs=["bold"]))
        collect_posts(args.target)
    
    if 'users' in args.collecting:
        print(colored("--- Users ---", "yellow", attrs=["bold"]))
        collect_users(args.target)
    
    if 'comments' in args.collecting:
        print(colored("--- Comments ---", "yellow", attrs=["bold"]))
        collect_comments(args.target)

    print(colored("DONE", "green", attrs=["bold"]))