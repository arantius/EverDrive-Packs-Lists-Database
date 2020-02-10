#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produce an organized collection based on an SMDB file.

Requires libarchive ( https://pypi.org/project/libarchive/ ).  E.g.:

  $ virtualenv --python=python3 env
  $ ./env/bin/pip install libarchive


Then, usage:

  $ ./env/bin/python build_pack.py <SMDB.txt> <destination> <source> [source] ...


The source(s) will be searched, including recursively inside archives.  Each
source may be a directory or an archive file.  So if you have, for some silly
reason, a RAR full of 7Z full of files, they'll all be found. The destination
will be filled with files from from the source, named as the the SMDB.txt file
dictates, wherever they are found.

The destination must be an existing directory.
"""

import glob
import hashlib
import io
import os
import pathlib
import shutil
import sys

import libarchive.exception
import libarchive.public


DB = {}
FOUND = set()

# TODO: Options.
#   Overwrite: never, if different.


def hash_file(path):
  h = hashlib.sha256()
  with open(path, 'rb') as f:
    for chunk in iter(lambda: f.read(4096), b''):
      h.update(chunk)
  return h.digest()


def hash_mem(buf):
  h = hashlib.sha256()
  h.update(buf)
  return h.digest()


def load_smdb(smdb):
  """Load data from an SMDB text file."""
  global DB
  DB = {}
  with open(smdb, 'r') as f:
    lines = f.readlines()
    lines.sort(key=lambda l: l[65:], reverse=True)
  for line in lines:
    sha256, filename, sha1, md5, crc = line.strip().split('\t', 4)
    if len(sha256) != 64:
      raise ValueError('Expected a SHA256 sum, got %r!' % sha256)
    DB[bytes(bytearray.fromhex(sha256))] = filename


def read_archive(source, destination):
  if isinstance(source, bytes):
    c = libarchive.public.memory_reader
  else:
    c = libarchive.public.file_reader

  with c(source) as i:
    for entry in i:
      # libarchive only streams, we can't re-read already-read blocks.
      # we want to read twice (1: hash, then 2: maybe write).
      # so read the whole file into memory?  ick.
      buf = b''
      for b in entry.get_blocks():
        buf += b

      try:
        read_archive(buf, destination)
      except (ValueError, libarchive.exception.ArchiveError):
        read_file(buf, destination)


def read_dir(source, destination):
  for path in glob.glob(os.path.join(source, '*')):
    if os.path.isdir(path):
      read_dir(path, destination)
    elif os.path.isfile(path):
      read_file(path, destination)


def read_file(source, destination):
  if isinstance(source, bytes):
    h = hash_mem(source)
    write_file(source, destination, h)
  elif os.path.isfile(source):
    try:
      read_archive(source, destination)
    except (ValueError, libarchive.exception.ArchiveError):
      h = hash_file(source)
      write_file(source, destination, h)
  else:
    print('What is it!?')


def write_file(source, destination, h):
  if h not in DB:
    return
  FOUND.add(h)
  out_path = os.path.join(destination, DB[h])
  out_dir = os.path.dirname(out_path)
  pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
  if os.path.exists(out_path):
    return
  if isinstance(source, bytes):
    with open(out_path, 'wb') as f:
      f.write(source)
  else:
    shutil.copyfile(source, out_path)


def main():
  args = sys.argv[1:]
  try:
    smdb = args.pop(0)
    destination = args.pop(0)
    sources = args
  except IndexError:
    return usage()

  if not os.path.isdir(destination):
    print('Error: destination %r does not exist' % destination, file=sys.stderr)
    return

  try:
    load_smdb(smdb)
  except ValueError as e:
    print('Error: could not read SMDB! (%s)' % e, file=sys.stderr)
    return

  for source in sources:
    if os.path.isdir(source):
      read_dir(source, destination)
    elif os.path.isfile(source):
      read_file(source, destination)

  print('Done.')
  print('SMDB lists %d files.' % len(DB))
  print(
      'Found %d files (%.2f%%).'
      % (len(FOUND), 100 * float(len(FOUND)) / float(len(DB))))


if __name__ == '__main__':
  main()
