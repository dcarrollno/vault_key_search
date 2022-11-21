#!/usr/bin/env python

import os
import json
import click
import shelve
import hvac
from hvac import exceptions


'''
This is a fast Vault secret key search program. This allows one to search
through all keys in a Vault instance finding the paths It builds a local
cache using shelve so you can search over and over without repeatitive api
calls to your Vault instance.

Be sure to export VAULT_ADDR and VAULT_TOKEN before using.
'''


def verify_vault_token():
    """function to verify our token against Vault and ensure it is valid"""

    assert client.lookup_token(os.environ.get('VAULT_TOKEN'))
    click.echo("Confirmed vault token is valid")

def recurse(key):

    if key.endswith('/'):
        result = client.list(path=key)
        #print(json.dumps(result['data']['keys'], indent=4))
        for x in result['data']['keys']:
            if x.endswith('/'):
                recurse(key+x)
            else:
                print(f'SECRET found at {x}')
                path = key+x
                print(f'Looking up secret at {path}')
                result=client.read(path)
                #print(json.dumps(result, indent=4))
                secret=(json.dumps(result['data']))
                s[path]=secret
    else:
        print(f'Looking up secret at {key}')
        result = client.read(key)
        #print(json.dumps(result, indent=4))
        secret=(json.dumps(result['data']))
        s[key]=secret

def search(key):
    print(f"Searching keys...")
    if key.endswith('/'):
        result = client.list(path=key)
        #print(json.dumps(result['data']['keys'], indent=4))
        for x in result['data']['keys']:
            if x.endswith('/'):
                recurse(key+x)
            else:
                print(f'SECRET found at {x}')
                path = key+x
                print(f'Looking up secret at {path}')
                result=client.read(path)
                #print(json.dumps(result, indent=4))
                secret=(json.dumps(result['data']))
                s[path]=secret
    else:
        print(f'Looking up secret at {key}')
        result = client.read(key)
        #print(json.dumps(result, indent=4))
        secret=(json.dumps(result['data']))
        s[key]=secret


def backup_secrets():

    print(f"Backing up from {os.environ.get('VAULT_ADDR')}")
    all_secrets = client.list(path='secret')
    all_secret_keys = (all_secrets['data']['keys'])
    for key in all_secret_keys:
        recurse('secret/'+key)

    s.close()

def search_vault(search):
    all_secrets = client.list(path='secret')
    all_secret_keys = (all_secrets['data']['keys'])
    for key in all_secret_keys:
        search('secret/'+key)


def read_secrets_from_shelve():
    for key,value  in s.items():
        print(f'{k}\t{v}')


def write_secret_to_vault(k,v):

    print(f'Restoring {k}')
    result = client.write(k, **v)


def restore_secrets():

    for k,v in s.items():
        val=json.loads(v)
        write_secret_to_vault(k,val)


@click.command()
@click.option("-b", is_flag=True, help="backup Vault secrets to shelve")
@click.option("-r", is_flag=True, help="restore Vault secrets to Vault instance")
@click.option("--search", "-s", help="search Vault secrets for key")
@click.option("-v", is_flag=True, help="verify token")

def main(b,r,s,v):
    """ Main Function """

    if b:
        click.echo("backup")
        backup_secrets()
    if r:
        click.echo("restore")
        restore_secrets()
    if v:
        verify_vault_token()

    if s:
       search_vault(search)

if __name__=='__main__':
    client = hvac.Client()
    s = shelve.open("secrets_export.db")
    main()
