#!/usr/bin/env python

import Queue, threading, shlex, time, re, os, random, sys, hashlib
from subprocess import Popen, PIPE, STDOUT


class Player(threading.Thread):
	player_path = '/usr/bin/mpg123'

	def __init__(self, queue=None):
		super(Player, self).__init__()
		self.queue     = queue
		_exec          = shlex.split('{0} -R PyPlayer'.format(self.player_path))
		self.player    = Popen(_exec, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
		self.handle    = self.player.stdout
		self.playing   = False
		self.id3       = False
		self.song_done = threading.Event()
		self.set_gain(60)
		self.daemon    = True
		self.start()

	def quit(self):
		self.send('QUIT')
		time.sleep(0.5)
		while True:
			self.player.poll()
			if not self.player.returncode is None:
				break
			time.sleep(0.25)
		try:
			self.player.kill()
		except OSError:
			pass
		sys.exit(0)

	def send(self, command):
		print >> sys.stderr, 'SENDING', command
		try:
			self.player.stdin.write('{0}\n'.format(command))
		except IOError:
			pass

	def load(self, filename):
		self.song_done.clear()
		print >> sys.stderr, 'loading', filename
		self.send('LOAD {0}'.format(filename))
		self.filename = os.path.normpath(os.path.realpath(filename))
		self.filehash = hashlib.sha224(self.filename).hexdigest()
		
	def loadpaused(self, filename):
		self.song_done.clear()
		print >> sys.stderr, 'loading (paused)', filename
		self.send('LOADPAUSED {0}'.format(filename))
		self.filename = os.path.normpath(os.path.realpath(filename))
		self.filehash = hashlib.sha224(self.filename).hexdigest()
 		
	def stop(self):
		self.send('STOP')

	def pause(self):
		if self.stopped:
			self.load(self.filename)
			self.jump_to(self.curframe)
		else:
			self.send('PAUSE')

	def jump_to(self, frame):
		self.send('JUMP {0}'.format(frame))

	def jump(self, seconds):
		jump_frames = int((self.played + seconds) * self.fps)
		self.jump_to(str(jump_frames))

	def jump_back_5(self):
		self.jump(-5)

	def jump_fwd_5(self):
		self.jump(5)

	def set_gain(self, gain):
		if gain > 100: gain = 100
		if gain < 1: gain = 0
		self.gain = gain
		self.send('VOLUME {0:d}'.format(gain))

	def vol_plus_x(self, x):
		n = self.gain + x
		self.set_gain(n)

	def vol_minus_x(self, x):
		n = self.gain - x
		self.set_gain(n)

	def vol_plus_1(self):
		self.vol_plus_x(1)

	def vol_minus_1(self):
		self.vol_minus_x(1)

	def vol_plus_10(self):
		self.vol_plus_x(10)

	def vol_minus_10(self):
		self.vol_minus_x(10)

	def restart(self):
		self.jump_to(0)

	def end(self):
		self.jump_to(self.frames + 1)

	def run(self):
		for line in iter(self.handle.readline, ''):
			code, data = (None,None)
			try:
				_p = line.strip().split(None, 1)
				code = _p[0]
				data = _p[1]
			except IndexError:
				continue

			if code == '@R':
				self.player_id = data

			elif code == '@F':
				p = map(str.strip, data.split(None, 3))
				try:
					f_played    = int(p[0])
					f_remaining = int(p[1])
					s_played    = float(p[2])
					s_remaining = float(p[3])

					self.curframe  = f_played
					self.played    = s_played
					self.remaining = s_remaining
					self.length    = s_played + s_remaining
					self.progress  = s_played / self.length
					self.frames    = f_played + f_remaining
					self.fps       = self.frames / self.length
				except Exception:
					pass

			elif code == '@I':
				p = data
				if p[0:4] == 'ID3:':
					self.title   = p[4:34].strip()
					self.artist  = p[34:64].strip()
					self.album   = p[64:94].strip()
					self.year    = p[94:98].strip()
					self.comment = p[98:128].strip()
					self.genre   = p[128:].strip()
					self.id3     = True
				else:
					#self.title   = p.strip()
					self.id3     = False

			elif code == '@P':
				'''
				0 - Playing has stopped. When 'STOP' is entered, or the mp3 file is finished.
				1 - Playing is paused. Enter 'PAUSE' or 'P' to continue.
				2 - Playing has begun again.
				3 - Song has ended.
				'''
				a = int(data.strip())
				if a == 0:
					self.stopped = True
					self.paused  = False
					self.playing = False
				elif a == 1:
					self.stopped = False
					self.paused  = True
					self.playing = False
				elif a == 2:
					self.stopped = False
					self.paused  = False
					self.playing = True
				elif a == 3:
					self.song_done.set()

			elif code == '@S':
				self.playing = True
				self.stopped = False
				self.paused  = False
				self.song_done.clear()
				p = map(str.strip, data.split(None, 11))

			elif code == '@E':
				print 'ERROR:', data

			else:
				pass

			self.queue.put(self.__dict__)


