# -*- coding: utf-8 -*-

import urllib, urllib2, shutil, os
import base, audio
from lib import util
import textwrap

class SpeechUtilComTTSBackend(base.SimpleTTSBackendBase):
	provider = 'speechutil'
	displayName = 'SPEECHUTIL.COM'
	ttsURL = 'http://speechutil.com/convert/wav?text={0}'
	canStreamWav = True
	interval = 100
	
	def __init__(self):
		self.process = None
		player = audio.WavPlayer(audio.UnixExternalPlayerHandler)
		base.SimpleTTSBackendBase.__init__(self,player,mode=base.SimpleTTSBackendBase.WAVOUT)

	def threadedSay(self,text):
		if not text: return
		sections = textwrap.wrap(text,100)
		for text in sections:
			outFile = self.player.getOutFile(text)
			if not self.runCommand(text,outFile): return
			self.player.play()

	def runCommand(self,text,outFile):
		url = self.ttsURL.format(urllib.quote(text.encode('utf-8')))
		req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36' })
		try:
			resp = urllib2.urlopen(req)
		except:
			util.ERROR('Failed to open speechutil.com TTS URL',hide_tb=True)
			return False
			
		with open(outFile,'wb') as out:
			shutil.copyfileobj(resp,out)
		return True

	def getWavStream(self,text):
		wav_path = os.path.join(util.getTmpfs(),'speech.wav')
		if not self.runCommand(text,wav_path): return None
		return open(wav_path,'rb')
			
	@staticmethod
	def available():
		return audio.WavPlayer.canPlay()
