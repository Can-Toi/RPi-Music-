#!/usr/bin/env python

from sys import argv
from playlist import Playlist, PlaylistItem
from NameSplit import nameSplit
from subprocess import Popen, PIPE, STDOUT, call
from threading import Thread

class MusicPlayer:
	cmd = ['mpg321','-R','RPi']
	volume = 0 #Specified in gain dB

	def __init__(self):
		self.init = True
		self.prun = False
		self.perror = 0
		self.playing = False
		self.playlist = Playlist()
		self.adjustVolume(0)

	def openPlayer(self):
		if not(self.prun):
			self.p = Popen(MusicPlayer.cmd,stdin=PIPE,stdout=PIPE,stderr=STDOUT)
			self.prun = True
			self.pout = Thread(target=self.readoutput)
			self.pout.daemon = True
			self.pout.start()
			return "Opened player"
		else:
			return "Player already open"

	def stopPlayer(self):
		if (self.prun):
			self.prun = False
			self.send("QUIT")
			self.p.terminate()
			self.p.wait()
			return "Stopped player"
		else:
			return "Player not running"

	def adjustVolume(self,adjust):
		try:
			MusicPlayer.volume = max(-100,min(0,MusicPlayer.volume+int(adjust)))
		except TypeError:
			return "[Error] Adjustment is not a number"
		finally:
			call(["amixer","-q","set","PCM","--",str(MusicPlayer.volume)+"dB"])
			return "Set volume to %s" % str(MusicPlayer.volume)+"dB"

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
		return "Quiting..."

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
						return "[ADD] Incorrect number of arguments!"
				elif user_in[1] == "DIRADD":
					if len(user_in[2:]) == 1:
						return self.playlist.add_dir(user_in[2])
					else:
						return "[DIRADD] Incorrect number of arguments!"
				elif user_in[1] == "SHOW": 
					return self.playlist.show()
				elif user_in[1] == "CLEAR":
					return self.playlist.clear()
				elif user_in[1] == "SHUFFLE":
					self.playlist.randomize()
					if self.playing:
						self.play()
					return "Randomized playlist:\n %s" % self.playlist.show()
				else:
					return "Unknown PLAYLIST command."
			except IndexError:
				return self.playlist.show()
			except:
				raise
		elif user_in[0] == "PLAY":
			return self.play()
		elif user_in[0] == "NEXT":
			return self.next()
		elif user_in[0] == "PREVIOUS":
			return self.prev()
		elif user_in[0] == "JUMP":
			try: return self.jump(user_in[1])
			except: return "No track number supplied."
		elif user_in[0] == "STOP":
			return self.stop()
		elif user_in[0] == "REPEAT":
			self.playlist.repeat = not(self.playlist.repeat)
			return "REPEAT is now %s" % ("ON" if self.playlist.repeat else "OFF")
		elif user_in[0] == "LIBRARY":
			try:
				return "%s" % self.playlist.setlibrary(user_in[1])
			except IndexError:
				return "Current library PATH is: %s" % Playlist.root
		elif user_in[0] == "VOLUME":
			try:
				if user_in[1] == "UP":
					return self.adjustVolume(1)
				elif user_in[1] == "DOWN":
					return self.adjustVolume(-1)
				else:
					return "Unknown argument"
			except IndexError:
				return "Current volume is %s" % str(MusicPlayer.volume) + "dB"
		else:
			return "Unknown command."

	def play(self):
		if self.playlist.len() > 0:
			if not(self.prun):
				self.openPlayer()
			self.send("LOAD %s" % self.playlist.get_path())
			self.playing = True
			return "Started playing"
		else:
			self.playing = False
			return "Cannot play, empty playlist."

	def stop(self):
		self.playing = False
		self.stopPlayer()
		return "Playback stopped."

	def next(self):
		if self.playlist.next() and self.playing:
			self.play()
			return "Now playing item %d: %s - %s" % (self.playlist.cursor+1,self.playlist[self.playlist.cursor].artist,self.playlist[self.playlist.cursor].title)
		else:
			self.stop()
			try:
				return "Moved cursor to item %d: %s - %s" % (self.playlist.cursor+1,self.playlist[self.playlist.cursor].artist,self.playlist[self.playlist.cursor].title)
			except IndexError:
				return "Can't move cursor, empty playlist"

	def prev(self):
		self.playlist.prev(self.playing)
		if self.playing:
			self.play()
		return "Moved to item: %s" % self.playlist.cursor + 1
	
	def jump(self,cursor):
		if self.playlist.jump(cursor):
			if self.playing:
				self.play()
			return "Jumped to %s" % cursor
		else:
			return "Error: [%r] is not a valid playlist track number" % cursor
	
def main(argv):
	player = MusicPlayer()
	
	while player.init:
		need_input = True
		while need_input:
			user_in = nameSplit(raw_input("RPiPlayer > ").strip("\n"))
			if len(user_in) > 0:
				need_input = False
		print("%s: %s" % (user_in[0],player.user_input(user_in)))
		need_input = True

# --------------------------------- #
if __name__ == "__main__":
	main(argv)
# --------------------------------- #
