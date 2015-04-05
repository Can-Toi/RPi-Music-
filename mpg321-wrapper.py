#!/usr/bin/env python

# This holds the MGP-wrapper class
# Currently no limit on the number independent players; 
# however, multiple 'mpg321' is untested


# Import modules
import subprocess
from threading import Thread
from Queue import Queue, Empty

import time, os, os.path
from sys import argv
import sys
from random import shuffle

def ReadPlayer(queue,stream):
	while True:
		streamout = stream.readline().strip("\n").split(" ")
		queue.put(streamout)

class MusicPlayer:
	nplayers = 0 					 # Count number of instances
	lroot = '/media/RPiLibrary/' 			 # Define the library root
	cmd = ['mpg321','-R','RPi'] # Define subprocess command

	def __init__(self):
		self.playlist = []
		self.cursor = 0
		self.playing = False
		self.repeat = False
		self.current = ''
		self.creation = time.strftime("%Y%m%d-%H%M")
		self.errors = 0
		self.maxerrors = 5
		self.p = subprocess.Popen(MusicPlayer.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		self.q = Queue()
		self.t = Thread(target=ReadPlayer, args=(self.q, self.p.stdout))
		self.t.daemon = True
		self.t.start()
	'''
	def enqueue_output(self, out, queue):
		for line in iter(out.readline, b''):
			queue.put(line)
		out.close()
	'''
	def __del__(self):
		self.p.terminate()
		
	def terminate(self):
		self.send('QUIT')
		self.p.terminate()
		self.p.wait()
	
	def add(self, fsong = "NO_SONG_SPECIFIED", R = False):
		if os.path.isfile(MusicPlayer.lroot + fsong):
			if fsong.endswith(".mp3"):	
				self.playlist.append(fsong)
			else:
				print("Only .mp3-files are currently supported")
		elif os.path.isdir(MusicPlayer.lroot + fsong):
			if R:
				slist = []
				for root, dirs, files in os.walk(MusicPlayer.lroot + fsong):
					for file in files:
						if file.endswith(".mp3"):
							slist.append(os.path.join(root, file)[len(MusicPlayer.lroot):])
			else:
				slist = []
				for file in os.listdir(MusicPlayer.lroot + fsong):
					if file.endswith(".mp3"):
						slist.append(os.path.join(fsong, file))
			for i in range(len(slist)):
				self.add(fsong = slist[i])
		else:
			print("Specified file %s does not exist..." % fsong)
	
	def shufflePlaylist(self):
		shuffle(self.playlist)
		self.cursor = 0
		
	def printPlaylist(self):
		print("Current Playlist:")
		if len(self.playlist) == 0:
			print ("(Playlist is empty)")
		for i in range(len(self.playlist)):
			print ("%s. %s" % (str(i+1),self.playlist[i]))
	
	def play(self):
		if self.cursor < len(self.playlist):
			self.send('LOAD %s' % (MusicPlayer.lroot + self.playlist[self.cursor]))
			#self.cursor = (self.cursor + 1) % len(self.playlist) #Ensures reset to 0 when last song is reached
			self.playing = True #if self.cursor != 0 else self.repeat
			print("%s / %s : %s" % (str(self.cursor + 1),len(self.playlist),self.playlist[self.cursor]))
		else:
			pass
	
	def next(self):
		self.cursor = (self.cursor + 1) % len(self.playlist)
		self.playing = True if self.playing == True and ((self.cursor != 0) or (self.repeat == True)) else False
		if self.playing:
			self.play()
	
	def previous(self):
		print "%s" % str(self.cursor),
		self.cursor = (self.cursor + len(self.playlist) - 1) % len(self.playlist)
		print("--> %s" % str(self.cursor))
	
	def send(self, mesg):
		self.p.stdin.write(mesg + '\n')
		self.p.stdin.flush()
	
	def poll(self):
		try:
			status = self.q.get(timeout=0.05)
			if status[0] == "@P":
				print("Got a P @P")
				self.next()
			elif status[0] == '@F':
				outstatus = "%r                                         \r" % status
				print outstatus,
				sys.stdout.flush()
			elif status == None:
				print("Geen output")
			else:
				with open('Log/' + self.creation + '-wrapper.log','a') as f:
					f.write(" | ".join(status) + "\n")
				if status[0] == "@E":
					self.errors += 1
					print("\nError detected! %r" % status)
					if self.errors > self.maxerrors:
						print "Caught too many errors, quiting..."
						self.send("QUIT")
						self.playing = False
						self.terminate()
		except KeyboardInterrupt:
			self.terminate()
			raise
		except:
			pass

def main(fsong,R=''):
	player = MusicPlayer()
	player.printPlaylist()
	player.add(fsong,False if R != 'R' else True)
	player.printPlaylist()
	player.shufflePlaylist()
	player.printPlaylist()
	player.play()
	while player.playing:
		try:
			player.poll()
			time.sleep(.01)
		except KeyboardInterrupt:
			player.terminate()
			raise

if __name__ == "__main__":
	if len(argv) == 2:
		main(argv[1])
	elif len(argv) == 3:
		main(argv[1],argv[2])
	else:
		print("Check command line arguments...")
