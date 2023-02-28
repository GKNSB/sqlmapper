#!/usr/bin/env python3

import uuid
import tqdm
import glob
import docker
import concurrent.futures
from os import remove
from tqdm import tqdm
from shutil import rmtree
from time import time, sleep
from argparse import ArgumentParser, FileType


def chunkify(original, numberOfItemsInChunk):
	for i in range(0, len(original), numberOfItemsInChunk):
		yield original[i:i + numberOfItemsInChunk]


def makeChunks(urlFile, chunkSize):
	urls = []
	with open(urlFile) as infile:
		for url in infile:
			urls.append(url.strip())

	print(f"[+] Total input is {len(urls)} lines")
	print(f"[+] Splitting in chunks of {chunkSize}")

	urlChunks = chunkify(urls, chunkSize)

	for urlchunk in urlChunks:
		filename = f"{str(uuid.uuid4())}.txt"

		with open(f"./inputs/{filename}", "w") as outfile:
			for aurl in urlchunk:
				outfile.write(f"{aurl}\n")


def cleanFolders():
	files = glob.glob("./inputs/*")
	for f in files:
		remove(f)
	
	files = glob.glob("./outputs/*")
	for f in files:
		try:
			remove(f)
		except IsADirectoryError:
			rmtree(f)


def is_container_running(container_name):
	docker_client = docker.from_env()

	try:
		container = docker_client.containers.get(container_name)
	except docker.errors.NotFound as exc:
		return False
	
	container_state = container.attrs["State"]
	return container_state["Status"] == "running"


def doWork(afile):
	client = docker.from_env()
	filename = afile.split("/")[-1]
	noExt = filename.split(".")[0]

	aContainer = client.containers.run("sqlmapper",
	command=f"-m /root/inputs/{filename} -c myconfig.ini --batch --smart --invalid-bignum --invalid-logical --invalid-string --output-dir /root/outputs/{noExt}",
	volumes=["/root/sqlmapper/inputs:/root/inputs", "/root/sqlmapper/outputs:/root/outputs"],
	labels=["sqlmapper"],
	auto_remove=True,
	detach=True)
	sleep(2)

	while is_container_running(aContainer.name):
		#print("Container still running...")
		sleep(5)

	return f"Done processing {afile}"


def gatherResults(outFile, outFolders):
	csvs = []
	
	for outFolder in outFolders:
		csv = glob.glob(f"{outFolder}/*.csv")
		csvs.extend(csv)

	with open(outFile, "w") as outfile:
		outfile.write("Target URL,Place,Parameter,Technique(s),Note(s)")

		for aCsv in csvs:
			with open(aCsv, "r") as a:
				for line in a:
					if "Technique(s)" not in line.strip() and len(line.strip()) > 1:
						outfile.write(line)


def main():
	parser = ArgumentParser(prog="sqlmapper.py", description="SQLMapper")
	parser.add_argument("urlFile", help="File containing URLs to be processed")
	parser.add_argument("-w", "--workers", action="store", dest="workers", help="Worker pool size", default=10)
	parser.add_argument("-c", "--chunk", action="store", dest="chunkSize", help="Chunk size for each worker", default=10)
	parser.add_argument("-o", "--outfile", action="store", dest="outFile", help="Output file location", default="./results.txt")

	args = parser.parse_args()

	cleanFolders()
	print("[+] Cleaned directories")

	makeChunks(args.urlFile, int(args.chunkSize))
	filesToProcess = glob.glob("./inputs/*")
	print(f"[+] Generated {len(filesToProcess)} file chunks (jobs)")

	print(f"[+] Executing jobs on {args.workers} workers")
	print("[+] Use 'docker ps -f \"label=sqlmapper\"' in another terminal to view the status of the containers")
	with tqdm(total=len(filesToProcess)) as progress:
		with concurrent.futures.ThreadPoolExecutor(max_workers=int(args.workers)) as executor:

			futures = {executor.submit(doWork, afile): afile for afile in filesToProcess}
			results = {}

			for future in concurrent.futures.as_completed(futures):
				#print(future.result())
				progress.update(1)

	outFolders = glob.glob("./outputs/*")
	gatherResults(args.outFile , outFolders)
	print(f"[+] Output written to {args.outFile}")


if __name__ == "__main__":
	startTime = time()
	main()
	stopTime = time()
	print(f"\n[+] Finished! Execution time: {int(stopTime - startTime)} seconds\n")
