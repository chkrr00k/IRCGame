
    #############################################################
    #                                                           #
    #   This program is relased in the GNU GPL v3.0 licence     #
    #   you can modify/use this program as you wish. Please     #
    #   link the original distribution of this software. If     #
    #   you plan to redistribute your modified/copied copy      #
    #   you need to relased the in GNU GPL v3.0 licence too     #
    #   according to the overmentioned licence.                 #
    #                                                           #
    #   "PROUDLY" MADE BY chkrr00k (i'm not THAT proud tbh)     #
    #                                                           #
    #############################################################
    #                                                           #
    #   I have tried to use a good mvc modelling while let-     #
    #   letting the maximum usability, modularity and mode-     #
    #   lling                                                   #
    #                                                           #
    #############################################################

import sys
import socket
import string
import ssl

import urllib.request
import re
from html.parser import HTMLParser
from game import Game, Player, Play
from time import sleep


HOST = "ayy.lmao"
NICK = "DUE"
IDENT = "qt"
REALNAME = "qt"
PASSWORD = ""
HELP_STRING = """HELP- .add to the url checking, .rem to remotion, .op .hop .voice and .deop .dehop .devoice .k supported"""

##MODEL
class Server:
    #private sock
    #private stringBuffer
    def __init__(self, server, port=6667, sslU=False):
        self.sock = socket.socket( )
        if sslU:
            self.sock = ssl.wrap_socket(self.sock)
        self.sock.connect((server, port))
        self.stringBuffer = ""
        
    def write(self, message):
        self.sock.send(bytes(message, "UTF-8"))
    
    def read(self):
        #old string + string just read.
        self.stringBuffer = self.stringBuffer + self.sock.recv(1024).decode("UTF-8")
        #split the string in corrispondence of "\n" to have a list of message ("\r" is still there)
        tmp = self.stringBuffer.split("\n")
        #
        self.stringBuffer = tmp.pop()
        return tmp

class Irc:
    #private ServerObj
    def __init__(self, server, port=6667, sslU=False):
        self.ServerObj = Server(server, port, sslU);
        self.lastString = ""
        self.messages = []
    
    def pingHandler(self, line):
        self.ServerObj.write("PONG " + (line.split() [1]) + "\r\n")

    def messageHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        channel = (tokLine[2]).strip()
        message = line.split(" :")[1]
        return nickName, channel, message

    def modeHandler(self, line):
        pass

    def quitHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        return nickName

    def partHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        channel = tokLine[2]
        if channel.startswith(":"):
            channel = channel[1:]
        return nickName, channel

    def joinHandler(self, line):
        tokLine = line.split()
        nickName = ((tokLine[0]).split("!")[0]).strip()[1:]
        channel = tokLine[2]
        if channel.startswith(":"):
            channel = channel[1:]
        return nickName, channel

    def inviteHandler(self, line):
        return (line.split(" ")[3])[1:]
    
    def sendMessage(self, channel, message):
        self.ServerObj.write("PRIVMSG " + channel + " :" + message +"\r\n")

    def sendNotice(self, channel, message):
        self.ServerObj.write("NOTICE " + channel + " :" + message +"\r\n")

    def setMode(self, channel, moded, mode, message=""):
        self.ServerObj.write("MODE " + channel + " " + mode + " " + moded + message +"\r\n")

    def readline(self):
        return self.ServerObj.read()

    def joinChannel(self, channel):
        self.ServerObj.write("JOIN " + channel + "\r\n") 

    def connect(self):
        self.ServerObj.write("NICK " + NICK + "\r\n")
        self.ServerObj.write("USER " + IDENT + " " + HOST + " ayy :" + REALNAME + "\r\n")

    def kick(self, channel, kicked, message=""):
        self.ServerObj.write("KICK " + channel + " " + kicked + " :" + message + "\r\n")

    def ban(self, channel, banned, message=""):
        self.setMode(channel, "+b", banned, " :" + message)

    def kickAndBan(self, channel, banned, message=""):
        self.kick(channel, banned, message)
        self.ban(channel, banned, message)

    def quit(self, message=""):
        self.ServerObj.write("QUIT" + " :" + message + "\r\n")

    def nickChange(self, newNick):
        self.ServerObj.write("NICK" + " " + newNick + "\r\n")

##CONTROLLER

irc = Irc("irc.example.net")

print("connecting")
irc.connect()
auth = 0
number = 0
channels = ["#channel"] #list of channels to join
instructionsOP = {".op" : "+o", ".deop" : "-o", ".protect" : "+a", ".deprotect" : "-a", ".voice" : "+v", ".devoice" : "-v", ".hop" : "+h", ".dehop" : "-h"} #possible commands form chat line (command : mode)
instructionsPR = {".k" : irc.kick, ".kb" : irc.kickAndBan, ".b" : irc.ban, ".quit" : irc.quit, ".nick" : irc.nickChange}
authorized = {"#channel" : {"admin" : [".op", ".deop", ".hop", ".dehop", ".voice",".devoice", ".k", ".quit"]}} #authorized users + list of commands they can use

gameP = None
play = None
owner = None
dealt = False
players = dict()

while 1:
    msgList = irc.readline()
    for msg in msgList:
        if msg.startswith("PING"):
            irc.pingHandler(msg.rstrip())
            print("PONGED")
            
        if msg.find("PRIVMSG") > -1:
            nick, chan, messS = irc.messageHandler(msg)
            print(nick, chan, messS)
#	    bot behaviour at messages promotion for user
            mess = messS.split(" ")
            if mess[0].strip() in instructionsOP and chan.strip().lower() in authorized :
                if nick in authorized[chan.strip().lower()]:
                    for mode in (authorized[chan.strip()])[nick.strip()]:
                        if mess[0].strip() == mode:
                            if len(mess) > 1:
                                irc.setMode(chan, mess[1], instructionsOP[mess[0].strip()])
                            else:
                                irc.setMode(chan, nick, instructionsOP[mess[0].strip()])

                            
            if mess[0].strip() in instructionsPR and chan.strip() in authorized :
                if nick in authorized[chan.strip()]:
                    for command in (authorized[chan.strip()])[nick.strip()]:
                        if mess[0].strip() == command:
                            if len(mess) == 2:
                                instructionsPR[mess[0]](chan, mess[1])
                            elif len(mess) > 2:
                                instructionsPR[mess[0]]("".join(str(x) for x in mess))
            
            if mess[0].startswith(".sta"):
                if len(mess) < 2:
                    irc.sendMessage(chan, "Insufficent paramether")

                elif gameP is None:
                    if int(mess[1]) > 10:
                        mess[1] = 10
                    gameP = Game(int(mess[1]))
                    owner = Player(nick, gameP, True)
                    players[owner.getName()] = owner
                    print(gameP)
                    irc.sendMessage(chan, "Game started")

                else:
                    irc.sendMessage(chan, "There is a game currently")

            if mess[0].startswith(".j"):
                if dealt:
                    irc.sendMessage(chan, "Already dealt")

                elif nick not in players:
                    players[nick] = Player(nick, gameP)
                    irc.sendMessage(chan, nick + " joined")
                    print(players)

                else:
                    irc.sendMessage(chan, "You are already in")

            if mess[0].startswith(".de"):

                if play is None and len(players) > 1:
                    play = Play(players.pop(owner.getName()))

                    for pl in players:
                        play.addPlayer(players[pl])
                    print(play)
                    dealt = True
                    irc.sendMessage(chan, "Dealt")
                    for st in gameP.print():
                        irc.sendMessage(chan, st)
                        sleep(0.49)

                else:
                    irc.sendMessage(chan, "Already dealt")

            if mess[0].startswith(".e"):

                if len(mess) < 4:
                    irc.sendMessage(chan, "Insufficent paramether")

                if dealt:
                    try:
                         play.play(nick, int(mess[1]), int(mess[2]), int(mess[3]))
                         for st in gameP.print():
                             irc.sendMessage(chan, st)
                             sleep(0.49)
                    except IOError as e:
                        irc.sendMessage(chan, "You can't do that: " + str(e))

                    if play.checkForWin():
                        irc.sendMessage(chan, nick + " lost")
                        players = dict()
                        play = None
                        gameP = None
                        dealt = False
                        owner = None

                else:
                    irc.sendMessage(chan, "You need to deal the game")

        if msg.find("NOTICE") > -1:
            nick, chan, mess = irc.messageHandler(msg)
            print(nick, chan, mess)

        if msg.find("INVITE") > -1:
            irc.joinChannel(irc.inviteHandler(msg))

        if msg.find("MODE") > -1:
            irc.modeHandler(msg)

        if msg.find("QUIT") > -1:
            nick = irc.quitHandler(msg)
            print(nick, " has quit")

        if msg.find("PART") > -1:
            nick, chan = irc.partHandler(msg)
            print(nick, " has left ", chan)

        if msg.find("JOIN") > -1:
            nick, chan = irc.joinHandler(msg)
            print(nick, " has join ", chan)
            
        if (number == 6) and not auth:
            auth = 1
            for chan in channels:
                irc.joinChannel(chan)
            irc.sendMessage("nickserv", "IDENTIFY %s" % (PASSWORD))
        number += 1

        

