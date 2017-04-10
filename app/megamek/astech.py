#!/home/lukasz/progi/python/botle/bin/python3
'''Megamek server administration page.
This is ALPHA quality software,
expect some bugs and glitches.
author: Łukasz Posadowski,  mail [at] lukaszposadowski.pl'''

# import subprocess, for launching jar files
import subprocess

# sleep may help with subprocess
from time import sleep

# import bottle
# remember to delete debug for production
from bottle import template, response, request, get, post, error, \
                   redirect, static_file, run, route, debug

# help with file uploading
import os
from pathlib import Path

# we have to append date to filename 
import time


# ----------------------------------------
# ------- HELPER FUNCTIONS ---------------
# ----------------------------------------

# megamek log files into lists
# TODO rewrite with WITH
def getFile(filename):
  '''filename -> list of last 22 lines'''
  try:
    logfile = open(filename,'r')
  except(FileNotFoundError):
    # when filename does not exist
    create_file = open(filename,'x').close()
    logfile = open(filename,'r')
  logfilelines = logfile.readlines()
  logfile.close()
  # we need only couple of last lines from the file
  lastlog = logfilelines[len(logfilelines)-22 : len(logfilelines)]
  lastlog.reverse()
  return lastlog 

# get a string from localtime
def stringTime():
  '''returns string: year-month-day__hour-minute-second_'''
  t = time.localtime()
  strtime = str(t[0]) + "-" + str(t[1]) + "-" + str(t[2]) + "__" + \
            str(t[3]) + "-" + str(t[4]) + "-" + str(t[5]) + "_"
  return strtime

# login and password (without encryption)
# looks secure so far... but have to be updated for
# database and encryption
def crede(l, p):
 if l == 'brathac' and p == 'deathabovefrom':
   return True
 else:
   return False


# ----------------------------------------
# ------- MAIN LOGIC ---------------------
# ----------------------------------------

# MegaMek server status and controls
# we have a class for a little namespace home 
class MegaTech:
  '''MegaMek server controls and status'''
  def __init__(self):
    self.ison = False                    # megamek is off by default 
    self.version = '0.42.1'              # megamek version
    self.port = 3477                     # port for megamek server
    self.domain = 'mek.solaris7.pl'      # nice site name
    self.from_save = False               # check if savegame is loaded
    self.save_dir = Path('./savegames/') # default save dir for megamek
  
  def start(self):
    '''starts MegaMek server'''
    self.process = subprocess.Popen('/usr/java/default/bin/java -jar MegaMek.jar -dedicated -port 3477'.split()) 
    #if not self.from_save:
    #  self.process = subprocess.Popen('/usr/java/default/bin/java -jar MegaMek.jar -dedicated -port 3477'.split()) 
    #elif self.from_save:
    #  self.process = subprocess.Popen('/usr/java/default/bin/java -jar MegaMek.jar -dedicated -port 3477 data/' + \
    #                                   .split()) 
    sleep(3)
    self.ison = True
  
  def stop(self):
    '''stops MegaMek server'''
    if self.ison == True:
      self.process.kill()
      self.ison = False
  
  def restart(self):
    '''quick restart with start and stop functions'''
    self.stop()
    sleep(1)
    self.start()

megatech = MegaTech()

# ----------------------------------------
# ------- BOTTLE STUFF -------------------
# ----------------------------------------

# site logo (thanks ManganMan) and other images
@route('/image/<filename>')
def image(filename):
  return static_file(filename, root='./img/', mimetype='image/png')

# a little login template
@get('/login')
def login():
  # username variable is required for header template
  username = request.get_cookie('administrator', secret='comstarwygra')
  # cookie with information about bad password
  bad_password = request.get_cookie('badPassword', secret='comstarprzegra')
  return template('login', badPass=bad_password, \
                           username=username)

# check credentials and redirect to other routes
@post('/login')
def check_login():
  # check if username and password isn't something like '/mmrestart'
  if request.forms.get('username').isalpha() and request.forms.get('password').isalpha():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if crede(username, password):
      # signed cookie for a period of time in seconds (about a day)
      response.set_cookie('administrator', username, max_age=87654, secret='comstarwygra')
      response.delete_cookie('badPassword')
      redirect('/')
    elif not crede(username,password):
      response.set_cookie('badPassword', 'nopass', max_age=21, secret='comstarprzegra')
      redirect('/login')
  else:
    # if login and/or password are not alpha, don't parse them
    # and redirect to login (just to be safe)
    response.set_cookie('badPassword', 'nopass', max_age=21, secret='comstarprzegra')
    redirect('/login')

# savegame upload form
@get('/saves')
def upload_save():
  username = request.get_cookie('administrator', secret='comstarwygra')
  if username:
    return template('saves', username=username, \
                             savegames=os.listdir('./savegames')) #, \
                             # removeSave=os.remove('.savegames/'+item))
  # an idea to remove saved games:
  # saves = os.lostdir(./savegames')
  # os.remove('.savegames/saves[index])
  elif not username:
    redirect('/login')

# checking and uploading files to savegames dir
@post('/saves')
def do_upload_save():
  username = request.get_cookie('administrator', secret='comstarwygra')
  if username:
    save_file = request.files.get('saved_game')
    name, ext = os.path.splitext(save_file.filename)
    if ext not in ('.gz'):
      # TODO nice info about wrong file extension
      print('WRONG SAVE :(')
    else:
      # TODO check if directory is present, create if nessesary;
      # add current time to file name, to avoid
      # incidental overwrites
      save_file.filename = stringTime() + save_file.filename
      save_file.save('./savegames', overwrite=True)
    sleep(1)
    redirect('/saves')
  elif not username:
    redirect('/login')

# map files upload form
@get('/maps')
def upload_map():
  username = request.get_cookie('administrator', secret='comstarwygra')
  if username:
    return template('maps', username=username, \
                            mapfiles=os.listdir('./data/boards/astech'))
  # an idea to remove saved games:
  # saves = os.lostdir(./savegames')
  # os.remove('.savegames/saves[index])
  elif not username:
    redirect('/login')

# checking and uploading files to savegames dir
@post('/maps')
def do_upload_map():
  username = request.get_cookie('administrator', secret='comstarwygra')
  if username:
    map_file = request.files.get('map_file')
    name, ext = os.path.splitext(map_file.filename)
    if ext not in ('.board'):
      # TODO nice info about wrong file extension
      print('WRONG MAP :(')
    else:
      # TODO check if directory is present, create if nessesary;
      # add current time to file name, to avoid
      # incidental overwrites
      map_file.save('./data/boards/astech', overwrite=True)
    sleep(1)
    redirect('/maps')
  elif not username:
    redirect('/login')

# main route
@route('/')
def administrator():
  username = request.get_cookie('administrator', secret='comstarwygra')
  if username:
    response.delete_cookie('badPassword')
    return template('administrator', username=username, \
                                     mmison=megatech.ison, \
                                     mmver=megatech.version, \
                                     port=str(megatech.port), \
                                     domain=megatech.domain, \
                                     getLogFile=getFile('logs/megameklog.txt'), \
                                     fromSave = megatech.from_save)
  elif not username:
    redirect('/login')

# a little functions doing bigger functions
# from MegaTech class
@route('/mmturnon')
def mmturnon():
  if request.get_cookie('administrator', secret='comstarwygra'):
    megatech.start()
  redirect('/')

@route('/mmturnoff')
def mmturnoff():
  if request.get_cookie('administrator', secret='comstarwygra'):
    megatech.stop()
  redirect('/')

@route('/mmrestart')
def mmrestart():
  if request.get_cookie('administrator', secret='comstarwygra'):
    megatech.restart()
  redirect('/')

@route('/logout')
def logoff():
  response.delete_cookie('administrator')
  redirect('/')

# finally - 404
@error(404)
def route404(error):
  username = request.get_cookie('administrator', secret='comstarwygra')
  return template('error404', username=username)

# ----------------
# main debug run
debug(True)
run(host='localhost', port=8080, reloader=True)

# main production run
# remember to delete debug import from bottle
#run(host='0.0.0.0', port=8080)

