#!/usr/bin/env python3

import sys
import socket
import string
import argparse
import os
import codecs

class ircbot():
	"""
		Object to handle a IRC session
	"""

	def __init__(self, host, port, channel, name, log, session):
		self.HOST = host
		self.PORT = port
		self.CHANNEL = channel
		self.NICK = name
		self.IDENT = name
		self.REALNAME = name
		self.LOG = channel[1:]+str(session)+log

		try:
			self.irc = socket.socket()
			self.irc.connect((self.HOST, self.PORT))
			print("Connected to %s\n" % self.HOST)
			self.irc.send(("NICK %s\r\n" % self.NICK).encode())

			self.irc.send(("USER %s %s bla :%s\r\n" % (self.IDENT,
									self.HOST,
									self.REALNAME)).encode())
			self.irc.send(("JOIN %s\r\n" % self.CHANNEL).encode())
			print("Joined %s as %s\n" % (self.CHANNEL, self.NICK))
		except Exception as e:
			print(e)
			sys.exit(1)

	def run(self):
		"""
			Main Application Loop
		"""

		# creating a tring variable to  dump irc data into
		readbuffer = ""
                mc = 0
                cc = 0
		# Everything the program does is going to happen here
		# an infinit loop of catching data and parsing it
		while True:
			readbuffer = readbuffer + self.irc.recv(1024).decode(encoding='UTF-8',errors='ignore')

			# We don't need everything the server sends to us
			# so we split it into a list and then drop the first part
			temp = readbuffer.split("\n")
			readbuffer = temp.pop()

			# Now we are going to step through the rest of the
			# lines in the list
			for line in temp:
				# Here I am going to strip off line endings
				# and split the string into a list using
				# whitespace as the seperator. It's not
				# necessary, but usefu for parsing commands
				# if you grow the bot that way
				linex = line.rstrip()
				linex = linex.split()
                                print(line)
				# PING PONG!
				# When the IRC Server sends us a ping we
				# best respond, or it will drop us
				if (linex[0] == "PING"):
					self.irc.send(bytes("PONG %s\r\n" % linex[1]))
				else:
                                        line = line[1:]
                                        if (not line.startswith(self.HOST)) and ("PRIVMSG" in line):
                                                uname = (line.split('!',1))[0]
                                                umsg = (line.split(':',1))[1]
                                                line = "<"+uname+"> : "+umsg 
					# And here we handle printing to the screen
					# or to a file
					        if self.LOG == 'stdout':
						        print(line)
					        else:
						        with codecs.open(self.LOG, "a", "utf-8") as log:
							        log.write(line)
                                                mc = mc+1
                                                if mc == 10:
                                                        os.system("git add "+self.LOG)
                                                        os.system("git commit -m \""+self.CHANNEL+str(cc)+"\"")
                                                        cc=cc+1
                                                        mc=0
                                                        os.system("git push origin master")

def parseargs():

	parser = argparse.ArgumentParser()
	parser.add_argument('-s', '--server', default='wolfe.freenode.net',
				help='dns address of the irc server. default=wolfe.freenode.net')
	parser.add_argument('-p', '--port', type=int, default=6667,
				help='port number of irc server. deault=6667')
	parser.add_argument('-c', '--channel', default='#python-unregistered',
				help='irc channel to join. default=#python-unregistered')
	parser.add_argument('-n', '--name', default='irc_logger_bot',
				help='how the bot will be identified in the channel. default=irc_logger_bot')
	parser.add_argument('-o', '--output', default='log.txt',
				help='file to write log to. default=stdout')
	parser.add_argument('-l', '--session', default=1,
				help='session number. default=1')
	
	return parser.parse_args()


if __name__ == '__main__':

	# Get the options from the parser
	opt = parseargs()

	# Create bot object and run it!
	bot = ircbot(opt.server, opt.port, opt.channel, opt.name, opt.output, opt.session)
	bot.run()
