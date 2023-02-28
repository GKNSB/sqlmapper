## sqlmapper
Launch different instances of sqlmap in docker containers against a list of targets. Monitor said containers, and keep launching new ones as a pool of workers. After execution all results are either in the respective folder per chunk, or in the output file specified.

First build, the image:
```
docker build -t sqlmapper .
```

The use with:

```
usage: sqlmapper.py [-h] [-w WORKERS] [-c CHUNKSIZE] [-o OUTFILE] urlFile

SQLMapper

positional arguments:
  urlFile               File containing URLs to be processed

optional arguments:
  -h, --help            show this help message and exit
  -w WORKERS, --workers WORKERS
                        Worker pool size
  -c CHUNKSIZE, --chunk CHUNKSIZE
                        Chunk size for each worker
  -o OUTFILE, --outfile OUTFILE
                        Output file location
```