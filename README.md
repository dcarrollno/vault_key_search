# vault_key_search
Vault key search with backgrounded indexer 

This is a simple search program for those who use Hashicorp Vault. 
This is an interactive cli that allows you to type in a simple phrase
and search Vault secret keys for that phrase. We assume you have your
VAULT_ADDR and VAULT_TOKEN env vars set correctly and pointed at your 
Vault instance. 

To begin run the program and it will call out to Vault and begin to index
your secret keys, saving them in a shelve db locally. Once that db has 
been created you can search for instant results. When you start the program 
up each time it will call out and build a new index but allow you to search
over and over without re-indexing. 

This is pretty handy for searching for keys you may have forgotten about or 
for locating keys and paths over a large Vault instance. 

For the moment we only support the secrets module but I may build in for others
including custom module paths. 


