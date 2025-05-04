import requests
import sys
import argparse
import json
from termcolor import colored
requests.packages.urllib3.disable_warnings()

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
parser.add_argument("-o", dest="outfile", help=f"Output to file", default=None)
args = parser.parse_args()

PROXIES = {"http":args.proxy,"https":args.proxy} if (args.proxy != None) else {}

def api_get_all(collection_uri):
    base_url = args.target + API_URI + collection_uri + "?per_page=10"
    total_pages = int(requests.get(base_url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"}, proxies=PROXIES, verify=False).headers.get("X-WP-TotalPages", 0))
    pages = []
    for page in range(1, total_pages+1):
        r = requests.get(base_url + f"&page={page}", headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"}, proxies=PROXIES, verify=False)
        pages.append(r.json())
    
    return pages

def check_connection(url):
    try:
        requests.get(url, verify=False)
        return True
    except:
        return False
        

def collect_media(url):
    result = []
    for group in api_get_all(COLLECTION_URIS['media']):
        for media in group:
            result.append(media['source_url'])
    return result

def collect_pages(url):
    result = []
    for group in api_get_all(COLLECTION_URIS['pages']):
        for media in group:
            result.append(media['link'])
    return result

def collect_posts(url):
    result = []
    for group in api_get_all(COLLECTION_URIS['posts']):
        for media in group:
            result.append(media['link'])
    return result

def collect_users(url):
    result = []
    for group in api_get_all(COLLECTION_URIS['users']):
        for media in group:
            result.append(media['link'])
    return result

def collect_comments(url):
    result = []
    for group in api_get_all(COLLECTION_URIS['comments']):
        for media in group:
            result.append(media['link'])
            result.append(media['content'])
    return result

if __name__ == '__main__':
    assert check_connection(args.target), colored("Could not connect to target.", "red", attrs=["bold"])
    print(f"Target Connection: " + colored(f"OK", "green", attrs=["bold"]))
    print(colored("Starting Collection", "white", attrs=["bold"]))
    
    data_to_save = []
    collect: str
    for collect in args.collecting:
        heading = colored(f"--- {collect.capitalize()} ---", "yellow", attrs=["bold"])
        data = []
        
        if collect == 'media':
            data = collect_media(args.target)
        
        elif collect == 'pages':
            data = collect_pages(args.target)
        
        elif collect == 'posts':
            data = collect_posts(args.target)
        
        elif collect == 'users':
            data = collect_users(args.target)
        
        elif collect == 'comments':
            data = collect_comments(args.target)
        
        # Print to stdout on each loop
        print(heading)
        for line in data:
            print(line)
            
        # store data to save to file at end
        if args.outfile:
            data_to_save.append({"heading": heading, "data": data})
        
        
    # dump all results to a file
    if args.outfile:
        try:
            with open(args.outfile, 'w') as f:
                for data in data_to_save:
                    f.write(data["heading"] + '\n')
                    f.write('\n'.join(data["data"]) + '\n')
        except FileNotFoundError:
            print(colored(f"ERROR: path '{args.outfile}' not valid! Saving to file failed!", "red", attrs=["bold"]))
        except PermissionError:
            print(colored(f"ERROR: insufficient permissions to write to '{args.outfile}'! Saving to file failed!", "red", attrs=["bold"]))

    print(colored("DONE", "green", attrs=["bold"]))