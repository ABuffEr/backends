# -*- coding: utf-8 -*-
import sys, wave, array, StringIO
from base import ThreadedTTSBackend

class SAPITTSBackend(ThreadedTTSBackend):
	provider = 'SAPI'
	displayName = 'SAPI (Windows Internal)'
	settings = {'voice':''}
	canStreamWav = True
	interval = 100
	speedMin = -10
	speedMax = 10
	speedMid = 0
	def __init__(self):
		import comtypes.client
		self.comtypesClient = comtypes.client
		self.SpVoice = comtypes.client.CreateObject("SAPI.SpVoice")
		self.update()
		self.threadedInit()
		
	def threadedSay(self,text):
		if not self.SpVoice: return
		self.SpVoice.Speak(text,1)

#	def getWavStream(self,text):
#		#Have SAPI write to file
#		stream = self.comtypesClient.CreateObject("SAPI.SpFileStream")
#		fpath = os.path.join(util.getTmpfs(),'speech.wav')
#		open(fpath,'w').close()
#		stream.Open(fpath,3)
#		self.SpVoice.AudioOutputStream = stream
#		self.SpVoice.Speak(text,0)
#		stream.close()
#		return open(fpath,'rb')
		
	def getWavStream(self,text):
		fmt = self.comtypesClient.CreateObject("SAPI.SpAudioFormat")
		fmt.Type = 22
		
		stream = self.comtypesClient.CreateObject("SAPI.SpMemoryStream")
		stream.Format = fmt
		self.SpVoice.AudioOutputStream = stream
		
		self.SpVoice.Speak(text,0)
		
		wavIO = StringIO.StringIO()
		self.createWavFileObject(wavIO,stream)
		return wavIO
	
	def createWavFileObject(self,wavIO,stream):
		#Write wave via the wave module
		wavFileObj = wave.open(wavIO,'wb')
		wavFileObj.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
		wavFileObj.writeframes(array.array('B',stream.GetData()).tostring())
		wavFileObj.close()
	
#	def createWavFileObject(self,wavIO,stream):
#		#Write wave headers manually
#		import struct
#		data = array.array('B',stream.GetData()).tostring()
#		dlen = len(data)
#		header = struct.pack(		'4sl8slhhllhh4sl',
#											'RIFF',
#											dlen+36,
#											'WAVEfmt ',
#											16, #Bits
#											1, #Mode
#											1, #Channels
#											22050, #Samplerate
#											22050*16/8, #Samplerate*Bits/8
#											1*16/8, #Channels*Bits/8
#											16,
#											'data',
#											dlen
#		)
#		wavIO.write(header)
#		wavIO.write(data)

	def stop(self):
		if not self.SpVoice: return
		self.SpVoice.Speak('',3)

	def voices(self):
		voices=[]
		v=self.SpVoice.getVoices()
		for i in xrange(len(v)):
			try:
				name=v[i].GetDescription()
			except COMError: #analysis:ignore
				pass
			voices.append(name)
		return voices

	def isSpeaking(self):
		return ThreadedTTSBackend.isSpeaking(self) or None
		
	def update(self):
		voice_name = self.setting('voice')
		if voice_name:
			v=self.SpVoice.getVoices()
			for i in xrange(len(v)):
				voice=v[i]
				if voice_name==voice.GetDescription():
					break
			else:
				# Voice not found.
				return
			self.SpVoice.voice = voice
		
	def close(self):
		del self.SpVoice
		self.SpVoice = None
		
	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')