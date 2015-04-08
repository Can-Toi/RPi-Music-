#!/usr/bin/env python

from sys import argv
from playlist import Playlist, PlaylistItem
from NameSplit import nameSplit
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

class MusicPlayer:
	cmd = ['mpg321','-R','RPi']

	def __init__(self):
		self.init = True
		self.prun = False
		self.perror = 0
		self.playing = False
		self.playlist = Playlist()

	def openPlayer(self):
		if not(self.prun):
			self.p = Popen(MusicPlayer.cmd,stdin=PIPE,stdout=PIPE,stderr=STDOUT)
			self.prun = True
			self.pout = Thread(target=self.readoutput)
			self.pout.daemon = True
			self.pout.start()
			return "openPlayer: Opened player"
		else:
			return "openPlayer: Player already open"
	
	def stopPlayer(self):
		if (self.prun):
			self.prun = False
			self.send("QUIT")
			self.p.terminate()
			self.p.wait()
			return "STOP: Stopped player"
		else:
			return "STOP: Player not running"
	
	def send(self,mesg):
		self.p.stdin.write(mesg + "\n")
		self.p.stdin.flush()
	
	def readoutput(self):
		while self.prun:
			get_output = self.p.stdout.readline().strip("\n").split(" ")
			if get_output[0] == "@P":
				if get_output[1] == "3":
					self.next()
			if get_output[0] == "@E":
				self.perror += 1
				if self.perror > 10:
					self.quit()
	
	def quit(self):
		self.stopPlayer()
		self.init = False
		return "quit: Quiting..."
		
	def user_input(self,user_in):	
		if user_in[0] == "QUIT":
			return self.quit()
		elif user_in[0] == "PLAYLIST":
			try:
				if user_in[1] == "LENGTH":
					return "Length: %d" % self.playlist.len()
				elif user_in[1] == "FILEADD":
					if 1 <= len(user_in[2:]) <= 4:
						self.playlist.add(PlaylistItem(*user_in[2:]))
						return "Adding..." #NEEDS EXIT SPECIFICATION
					else:
						return "PLAYLIST ADD: Incorrect number of arguments!"
				elif user_in[1] == "DIRADD":
					if len(user_in[2:]) == 1:
						return self.playlist.add_dir(user_in[2])
					else:
						return "PLAYLIST DIRADD: Incorrect number of arguments!"
				elif user_in[1] == "SHOW": 
					return self.playlist.show()
				elif user_in[1] == "CLEAR":
					self.playlist.clear()
				elif user_in[1] == "SHUFFLE":
					self.playlist.randomize()
					if self.playing:
						self.play()
				else:
					print("Unknown PLAYLIST command.")
			except IndexError:
				return self.playlist.show()
			except:
				raise
		elif user_in[0] == "PLAY":
			self.play()
		elif user_in[0] == "NEXT":
			self.next()
		elif user_in[0] == "PREVIOUS":
			self.prev()
		elif user_in[0] == "JUMP":
			try: self.jump(user_in[1])
			except: print("No track number supplied.")
		elif user_in[0] == "STOP":
			self.stop()
		elif user_in[0] == "REPEAT":
			self.playlist.repeat = not(self.playlist.repeat)
			print("REPEAT is now %s" % ("ON" if self.playlist.repeat else "OFF"))
		else:
			print("Unknown command.")
		
	def play(self):
		if self.playlist.len() > 0:
			if not(self.prun):
				self.openPlayer()
			self.send("LOAD %s" % self.playlist.get_path())
			self.playing = True
		else:
			print("Error: Cannot play, empty playlist.")
	
	def stop(self):
		self.playing = False
		self.stopPlayer()
	
	def next(self):
		if self.playlist.next() and self.playing:
			self.play()
		else:
			self.stop()
	
	def prev(self):
		self.playlist.prev(self.playing)
		if self.playing:
			self.play()
	
	def jump(self,cursor):
		if self.playlist.jump(cursor):
			if self.playing:
				self.play()
		else:
			print("Error: [%r] is not a valid playlist track number" % cursor)
	
def main(argv):
	player = MusicPlayer()
	
	while player.init:
		need_input = True
		while need_input:
			user_in = nameSplit(raw_input("RPiPlayer > ").strip("\n"))
			if len(user_in) > 0:
				need_input = False
		print(player.user_input(user_in))
		need_input = True

# --------------------------------- #
if __name__ == "__main__":
	main(argv)
# --------------------------------- #
