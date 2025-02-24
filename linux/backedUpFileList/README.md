# Backup Up File List for Linux

Warning: this code is provided on a best effort basis and is not in any way officially supported or sanctioned by Cohesity. The code is intentionally kept simple to retain value as example code. The code in this repository is provided as-is and the author accepts no liability for damages resulting from its use.

This is a binary version of backedUpFileList for Linux. It enumerates the files that are available for restore from the specified server/job. The file list is written to an output text file.

## Download the tool

Run these commands from a terminal to download the script(s) into your current directory

```bash
# Begin download commands
curl -O https://raw.githubusercontent.com/bseltz-cohesity/scripts/master/linux/backedUpFileList/backedUpFileList
chmod +x backedUpFileList
# End download commands
```

## Examples

Place all files in a folder together. then, run the main script like so:

To list what versions are available:

```bash
./backedUpFileList -v mycluster \
                   -u myuser \
                   -d mydomain.net \
                   -s server1.mydomain.net \
                   -j 'My Backup Job' \
                   -l
```

To use a specific job run ID:

```bash
./backedUpFileList -v mycluster \
                   -u myuser \
                   -d mydomain.net \
                   -s server1.mydomain.net \
                   -j 'My Backup Job' \
                   -r 123456
```

To choose the backup at or after the specified file date:

```bash
./backedUpFileList -v mycluster \
                   -u myuser \
                   -d mydomain.net \
                   -s server1.mydomain.net \
                   -j 'My Backup Job' \
                   -f '2020-06-30 13:00:00'
```

## Parameters

* -v, --vip: name of Cohesity cluster to connect to
* -u, --username: short username to authenticate to the cluster
* -d, --domain: active directory domain of user (default is local)
* -i, --useApiKey: use API key for authentication
* -pwd, --password: (optional) password for Cohesity user
* -s, --sourceserver: name of server to inspect (repeat for multiple)
* -j, --jobname: name of protection job to run
* -l, --showversions: show available versions
* -t, --start: show versions after date
* -e, --end: show versions before date
* -r, --runid: use specific run ID
* -f, --filedate: (optional) date to inspect (next backup after date will be inspected)
* -p, --startpath: (optional) start listing files at path (default is /)
* -n, --noindex: (optional) do not use the index (otherwise index usage will be automatic)
* -f, --forceindex: (optional) force use the index (otherwise index usage will be automatic)
* -ss, --showstats: (optional) include file date and size in the output
* -nt, --newerthan: (optional) show files added/modified in the last X days
