# Groot Query using Python

Warning: this code is provided on a best effort basis and is not in any way officially supported or sanctioned by Cohesity. The code is intentionally kept simple to retain value as example code. The code in this repository is provided as-is and the author accepts no liability for damages resulting from its use.

This python script executes a Groot query and exports the output to a TSV file.

## Components

* grootQuery.py: the main python script
* pyhesity.py: the Cohesity REST API helper module

You can download the scripts using the following commands:

```bash
# download commands
curl -O https://raw.githubusercontent.com/bseltz-cohesity/scripts/master/groot/python/grootQuery/grootQuery.py
curl -O https://raw.githubusercontent.com/bseltz-cohesity/scripts/master/python/pyhesity.py
chmod +x grootQuery.py
# end download commands
```

## Running the script

Place both files in a folder together and run the main script like so:

```bash
# example
./grootQuery.py -v mycluster -u myuser -d mydomain.net -q myquery.sql -o myoutput.tsv
# end example
```

## Queries

See <https://github.com/bseltz-cohesity/scripts/tree/master/groot/queries> for example queries

## Authentication Parameters

* -v, --vip: (optional) DNS or IP of the Cohesity cluster to connect to (default is helios.cohesity.com)
* -u, --username: (optional) username to authenticate to Cohesity cluster (default is helios)
* -d, --domain: (optional) domain of username (defaults to local)
* -i, --useApiKey: (optional) use API key for authentication
* -pwd, --password: (optional) password or API key
* -np, --noprompt: (optional) do not prompt for password
* -mcm, --mcm: (optional) connect through MCM
* -c, --clustername: (optional) helios/mcm cluster to connect to

## Other Parameters

* -q, --queryfile: path to sql file containing query
* -o, --outfile: path to output tsv file

## Prerequisites

This python script requires two python modules (requests, psycopg2-binary) that are not present in the standard library. These can be installed in one of the following ways:

Using yum:

```bash
yum install python-requests python-psycopg2
```

Using pip:

```bash
pip install requests
pip install psycopg2
```

Using easy_install:

```bash
easy_install requests
easy_install psycopg2
```
