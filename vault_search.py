#!/usr/bin/env python

import os
import re
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import shelve
import typing
import json
import hvac
from hvac import exceptions


# Local cache of Vault keys
TEMP_VAULT_INDEX ='.tmp_vault_index.db'
VAULT_INDEX = '.vault_index.db'


class Search():
    """Background Indexer responsible for building and refreshing cache"""


    def __init__(self):
        self.client = hvac.Client()
        self.index = shelve.open(TEMP_VAULT_INDEX,'c')
        thread = threading.Thread(target=self.indexer, args=())
        thread.daemon = False                # Daemonize thread
        thread.start()

    def recurse(self, key):
        if key.endswith('/'):
            result = self.client.list(path=key)
            for x in result['data']['keys']:
                if x.endswith('/'):
                    self.recurse(key+x)
                else:
                    path = key+x
                    result = self.client.read(path)
                    secret = (json.dumps(result['data']))
                    self.index[path] = secret
        else:
            # this must be a secret
            next

    def indexer(self):
        # here we call Vault and index as a background task
        print(f"Indexing secrets...")
        all_secrets = self.client.list(path='secret')
        all_secret_keys = (all_secrets['data']['keys'])
        threads = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for key in all_secret_keys:
                threads.append(executor.submit(self.recurse, 'secret/'+key))

        self.index.close()
        os.rename(TEMP_VAULT_INDEX,VAULT_INDEX)


    def search(self, search_term):
        print(f"Searching for {search_term}...")

        try:
            s = shelve.open(VAULT_INDEX,'r')
            for k,v in s.items():
                if search_term in k:
                    print(f'Found {search_term} in {k}')
        except:
            # no locally cached db
            print(f'Unable to locate the local cache file at {VAULT_INDEX}. Please allow indexing to complete')

def handler(self, signum):
    exit(1)


def main():
    """ Main CLI """
    key_search = Search()
    signal.signal(signal.SIGINT, handler)
    while True:
        print(f'Press ctrl-c to exit')
        print(f'Vault key to search for: ')
        key_to_find = input()
        key_search.search(key_to_find)


if __name__=='__main__':
    main()
