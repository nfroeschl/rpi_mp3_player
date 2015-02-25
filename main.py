#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2015 Unknown <nobby@nobbylinux>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import os, sys
import pygame
import platform
import Queue
import logging as log
from album import album
from player import Player
"""
aspect_scale.py - Scaling surfaces keeping their aspect ratio
Raiser, Frank - Sep 6, 2k++
crashchaos at gmx.net

This is a pretty simple and basic function that is a kind of
enhancement to pygame.transform.scale. It scales a surface
(using pygame.transform.scale) but keeps the surfaces aspect
ratio intact. So you will not get distorted images after scaling.
A pretty basic functionality indeed but also a pretty useful one.

Usage:
is straightforward.. just create your surface and pass it as
first parameter. Then pass the width and height of the box to
which size your surface shall be scaled as a tuple in the second
parameter. The aspect_scale method will then return you the scaled
surface (which does not neccessarily have the size of the specified
box of course)

Dependency:
a pygame version supporting pygame.transform (pygame-1.1+)
"""

def aspect_scale(img,(bx,by)):
	""" Scales 'img' to fit into box bx/by.
	 This method will retain the original images aspect ratio """
	ix,iy = img.get_size()
	if ix > iy:
		# fit to width
		scale_factor = bx/float(ix)
		sy = scale_factor * iy
		if sy > by:
			scale_factor = by/float(iy)
			sx = scale_factor * ix
			sy = by
		else:
			sx = bx
	else:
		# fit to height
		scale_factor = by/float(iy)
		sx = scale_factor * ix
		if sx > bx:
			scale_factor = bx/float(ix)
			sx = bx
			sy = scale_factor * iy
		else:
			sy = by

	return pygame.transform.scale(img, (int(sx),int(sy)))
def AAfilledRoundedRect(surface,rect,color,radius=0.4,text='',size=72):

	"""
	AAfilledRoundedRect(surface,rect,color,radius=0.4)

	surface : destination
	rect    : rectangle
	color   : rgb or rgba
	radius  : 0 <= radius <= 1
	"""

	rect         = pygame.Rect(rect)
	color        = pygame.Color(*color)
	alpha        = color.a
	color.a      = 0
	pos          = rect.topleft
	center 		 = rect.center
	rect.topleft = 0,0
	rectangle    = pygame.Surface(rect.size,pygame.SRCALPHA)
	font = pygame.font.SysFont("fontawesome", size)
	renderedText = font.render(text, True, (255, 128, 128))
	
	circle       = pygame.Surface([min(rect.size)*3]*2,pygame.SRCALPHA)
	pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
	circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

	radius              = rectangle.blit(circle,(0,0))
	radius.bottomright  = rect.bottomright
	rectangle.blit(circle,radius)
	radius.topright     = rect.topright
	rectangle.blit(circle,radius)
	radius.bottomleft   = rect.bottomleft
	rectangle.blit(circle,radius)

	rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
	rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

	rectangle.fill(color,special_flags=pygame.BLEND_RGBA_MAX)
	rectangle.fill((255,255,255,alpha),special_flags=pygame.BLEND_RGBA_MIN)
	sr = surface.blit(rectangle,pos)
	log.debug(pos)
	log.debug(center)
	log.debug(renderedText.get_width())
	TextRect = renderedText.get_rect()
	TextRect.center = center
	sr = surface.blit(renderedText,TextRect)
	return sr 
 
def getAlbums():
	return Albums

def showcover(cover):

	img = pygame.image.load(cover)

	img = aspect_scale(img, (w, h))
	screen.blit(img,(0,0))



if __name__ == '__main__':
	FORMAT = '%(asctime)-15s %(message)s'
	log.basicConfig(format=FORMAT, level=log.DEBUG)
	pygame.mixer.pre_init(44100, -16, 2, 4096) # setup mixer to avoid sound lag

	pygame.init()
	white = (255, 64, 64)
	w = 800
	h = 480
	currentAlbum = 0
	if (platform.machine() == "armv7h"):
		os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
		screen = pygame.display.set_mode((w, h),pygame.FULLSCREEN,32)
	else:
		screen = pygame.display.set_mode((w, h),0,32)

	screen.fill((white))

	Albums = []

	queue = Queue.Queue()
	rootDir = '../../emilMP3/music'
	for dirName in os.listdir(rootDir):
		log.debug('Found directory: %s' % dirName)
		Albums.append(album(os.path.join(rootDir,dirName)))

	log.debug(Albums)
	ButtonRight = AAfilledRoundedRect(screen,(710,20,80,80),(200,20,20),0.5,unichr(0xf105),80)
	ButtonLeft = AAfilledRoundedRect(screen,(490,20,80,80),(200,20,20),0.5,unichr(0xf104),80)
	ButtonUp = AAfilledRoundedRect(screen,(710,140,80,80),(200,20,20),0.5,unichr(0xf106),80)
	ButtonDown = AAfilledRoundedRect(screen,(490,140,80,80),(200,20,20),0.5,unichr(0xf107),80)
	ButtonVolumeUp = AAfilledRoundedRect(screen,(710,260,80,80),(200,20,20),0.5,unichr(0xf028))
	ButtonVolumeDown = AAfilledRoundedRect(screen,(490,260,80,80),(200,20,20),0.5,unichr(0xf027))
	#ButtonStop = AAfilledRoundedRect(screen,(710,380,80,80),(200,20,20),0.5,unichr(0xf04d),50)
	ButtonPlay = AAfilledRoundedRect(screen,(490,380,300,80),(200,20,20),0.5,unichr(0xf04c),50)
	showcover(Albums[currentAlbum].getCover())
	player = Player(queue)
	#song = Albums[currentAlbum].getNextSong()
	pygame.display.flip()
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				# Set the x, y postions of the mouse click
				x, y = event.pos
				if ButtonUp.collidepoint(x, y):
					log.debug("up")
					song = Albums[currentAlbum].getPrevSong()
					player.load(os.path.normpath(os.path.realpath(song)))
				elif ButtonDown.collidepoint(x ,y):
					song = Albums[currentAlbum].getNextSong()
					player.load(os.path.normpath(os.path.realpath(song)))
					log.debug("down")
				elif ButtonLeft.collidepoint(x ,y):
					log.debug("left")
					currentAlbum += 1
					showcover(Albums[currentAlbum].getCover())
					player.stop()
					song = Albums[currentAlbum].getNextSong()
					player.loadpaused(os.path.normpath(os.path.realpath(song)))
					ButtonPlay = AAfilledRoundedRect(screen,(490,380,300,80),(200,20,20),0.5,unichr(0xf04c),50)
				elif ButtonRight.collidepoint(x ,y):
					log.debug("right")
					currentAlbum -= 1
					showcover(Albums[currentAlbum].getCover())
					player.stop()
					song = Albums[currentAlbum].getNextSong()
					player.loadpaused(os.path.normpath(os.path.realpath(song)))
					ButtonPlay = AAfilledRoundedRect(screen,(490,380,300,80),(200,20,20),0.5,unichr(0xf04c),50)
				elif ButtonVolumeUp.collidepoint(x ,y):
					log.debug("volumeup")
					player.vol_plus_10()
				elif ButtonVolumeDown.collidepoint(x ,y):
					log.debug("volumedown")
					player.vol_minus_10()
				elif ButtonPlay.collidepoint(x ,y):
					log.debug("play")
					if player.playing:
						player.pause()
						ButtonPlay = AAfilledRoundedRect(screen,(490,380,300,80),(200,20,20),0.5,unichr(0xf04c),50)
					if player.paused:
						player.pause()
						ButtonPlay = AAfilledRoundedRect(screen,(490,380,300,80),(200,20,20),0.5,unichr(0xf04b),50)
					if player.stopped:
						ButtonPlay = AAfilledRoundedRect(screen,(490,380,300,80),(200,20,20),0.5,unichr(0xf04b),50)
						song = Albums[currentAlbum].getNextSong()
						player.load(os.path.normpath(os.path.realpath(song)))
		font = pygame.font.SysFont("arial", 20)
		if queue.qsize() > 0:
		# Update all of the simple widgets from data in our queue
			#log.debug("Queue")
			item = queue.get()
			#print item

			if ('progress' in item):
				renderedText = font.render(str(100-int(item['progress']*100)), True, (0, 0, 0), (255,255,255))
				#screen.fill((255,255,255))
				#screen.fill((255,255,255), rect=renderedText.get_rect(topleft=(0,0)))
				screen.blit(renderedText,(0,0))
		#pygame.transform.rotate(ButtonPlay,10)
		pygame.display.flip()
		pygame.time.wait(100	)
 
