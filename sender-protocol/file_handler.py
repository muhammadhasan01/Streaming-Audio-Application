import os
import shutil

class Chunk:
	def tmp_path(self):
		return "{}/{}".format(self.tmpdir, str(self.sequence).zfill(5))

	def __init__(self, sequence, content, tmpdir):
		self.tmpdir = tmpdir
		self.sequence = sequence
		self.path = self.tmp_path()
		self.content = content

	def write_to_tmp(self):
		f = open(self.path, 'wb')
		f.write(self.content)
		f.close()

class File:
	def __init__(self, fname):
		self.outdir = './out'
		self.tmpdir = './tmp'

		if os.path.isdir(self.tmpdir):
			shutil.rmtree(self.tmpdir, ignore_errors=False, onerror=None)

		os.mkdir(self.tmpdir)

		self.fname = fname
		self.chunk_paths = set()

	def set_name(self, fname):
		self.fname = fname

	def add_chunk(self, sequence, content):
		c = Chunk(sequence, content, self.tmpdir)
		if c.path not in self.chunk_paths:
			self.chunk_paths.add(c.path)
			c.write_to_tmp()

	def merge_chunks(self):
		out = self.outdir + "/" + self.fname
		filenames = [path for path in self.chunk_paths]
		filenames.sort()
		with open(out, 'wb') as outfile:
			for fname in filenames:
				with open(fname, 'rb') as infile:
					for line in infile:
						outfile.write(line)

	def __del__(self):
		if os.path.isdir(self.tmpdir):
			shutil.rmtree(self.tmpdir, ignore_errors=False, onerror=None)