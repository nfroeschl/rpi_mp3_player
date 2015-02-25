import os, Queue
import logging as log

class album:
	""" Class doc """
	
	def __init__ (self, path):
		self.playlist = []
		cover = ""
		self.currentsong = 0
		print path
		for filename in os.listdir(path):
			log.debug(filename)
			if os.path.splitext(filename)[1] == '.jpg':
				self.cover = os.path.join(path,filename)
				log.debug("found:"+self.cover)
			elif os.path.splitext(filename)[1] == '.mp3':
				self.playlist.append(os.path.join(path,filename))
		self.playlist.sort()
	
	def getNextSong(self):
		song = self.playlist[self.currentsong % len(self.playlist)]
		self.currentsong += 1
		return song

	def getPrevSong(self):
		song = self.playlist[self.currentsong % len(self.playlist)]
		self.currentsong -= 1
		return song
		
	def getCover(self):
		log.debug("getCover():"+self.cover)
		return self.cover
			
	def getPlaylist(self):
		return self.playlist;
