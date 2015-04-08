from subprocess import check_output, CalledProcessError
from time import time
import os, os.path
from random import shuffle

class PlaylistItem:
	def __init__(self,path,artist="Unknown",title="Unknown",album="Unknown",track="999",l=True):
		if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
			path = path[1:-1]
		if os.path.isfile(Playlist.root + path):
			self.path = path
			self.artist = artist
			self.title = title
			self.album = album
			self.track = track
			if l:
				artist, title, album, track = self.mp3info(path).split(";")
				self.artist = artist if self.artist == "Unknown" and artist != "" else self.artist
				self.title = title if self.title == "Unknown" and title != ""  else self.title
				self.album = album if self.album == "Unknown" and album != "" else self.album
				self.track = track if self.track == "999" and track != "" else self.track
			self.artist = self.artist if len(self.artist) <= 30 else self.artist[:27] + "..."
			self.title = self.title if len(self.title) <= 30 else self.title[:27] + "..."
			self.album = self.album if len(self.album) <= 30 else self.album[:27] + "..."
		else:
			print("Error: File not found")

	def mp3info(self,path):
		try:
			return check_output(["mp3info",Playlist.root + path,"-p","%a;%t;%l;%n"],stderr=None)
		except CalledProcessError:
			return ";;;"
	def unpack(self):
		return [self.path,self.artist,self.title,self.album,self.track]

class Playlist(list):
	root = "/media/RPiLibrary/"
	#root = "/media/sebastiaan/Data/Music/"
	def __init__(self):
		self.cursor = 0
		self.repeat = True

	def setlibrary(self,path):
		if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
			path = path[1:-1]
		if os.path.isdir(path):
			Playlist.root = path
			return "Set library PATH to %s" % path
		else:
			return "Error PATH not found"

	def add(self,item):
		self.append(item)

	def add_dir(self,fdir):
		if fdir.startswith('"') and fdir.endswith('"'):
			fdir = fdir[1:-1]
		adir = Playlist.root + fdir
		if os.path.isdir(adir):
			addition = Playlist()
			slist = []
			for root, dirs, files in os.walk(adir):
				for file in files:
					if file.endswith(".mp3"):
						slist.append(os.path.join(root, file)[len(Playlist.root):])
			for item in slist:
				addition.add(PlaylistItem(item))
			#addition.sort(key=lambda item: str.lower(item.title))
			#addition.sort(key=lambda item: int(item.track))
			#addition.sort(key=lambda item: str.lower(item.album))
			#addition.sort(key=lambda item: str.lower(item.artist))
			addition.sort(key=lambda item: (item.artist,item.album,int(item.track)))
			self.extend(addition)
			return "[ADDDIR]: Added directory %r" % fdir
		else:
			return "[ADDDIR] Directory not found"

	def save(self):
		pass

	def load(self):
		pass

	def len(self):
		return len(self)

	def clear(self):
		for i in range(len(self)):
			self.pop()
		self.cursor = 0
		return "Playlist cleared"

	def show(self):
		result ="{0:^3} {1:>5}. {2:<30} {3:<30} {4:<30}\n".format("","Track","Artist","Title","      Album")
		i = 1
		for item in self:
			if (item.artist == "Unknown") and (item.title == "Unknown") and (item.album == "Unknown"):
				output = "Path: " + item.path if len(item.path) <= 85 else "Path: (...)" + item.path[-80:]
			else:
				nr = item.track if item.track != "999" else ""
				output = "{0:<30} {1:<30} {3:>5} {2:<30}".format(item.artist,item.title,item.album,"("+nr+")")
			cur = "" if i != self.cursor + 1 else ">>>"
			result += "{0:^3} {1:>5}. {2}\n".format(cur,str(i),output)
			i += 1
		return result

	def get_path(self):
		self.lplay = time()
		return (Playlist.root + self[self.cursor].path)

	def prev(self,playing):
		if self.cursor > 0:
			if self.lplay and playing:
				self.cursor -= 1 if (time()-self.lplay) <= 5 else 0
			else:
				self.cursor -= 1

	def next(self):
		if self.cursor < len(self) - 1:
			self.cursor += 1
			return True
		else:
			self.cursor = 0
			return self.repeat

	def jump(self,cursor):
		try:
			if 0 < int(cursor) <= len(self):
				self.cursor = int(cursor) - 1
				return True
			else:
				return False
		except:
			return False

	def randomize(self):
		shuffle(self)
		self.cursor = 0
