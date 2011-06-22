
from django.template import Context, loader, RequestContext
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
#from mysite.answers.models import Question, Answer, UserProfile, Tag, VoteQuestion, VoteAnswer, Comment, Badge, EarnedBadge, View
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render_to_response
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils import simplejson
from django.db.models import Q, Max, Sum
from datetime import datetime
from bbcstats.bbc.models import User, Entry, PitcherEntry, PlayerEntry, UserStats
from django.core.exceptions import ObjectDoesNotExist

import teams
import re
import urllib
from BeautifulSoup import *

def ipFrac(i):
	return int(round((float(i)-round(float(i)))*10,0))


def addIP(i1,i2):

	ipf1 = ipFrac(i1)
	ipf2 = ipFrac(i2)
	print ipf1
	print ipf2
	ipf = ipf1+ipf2
	print i1
	print i2
	if ipf == 0:
		return (float(i1)+float(i2))
	if ipf == 1:
		return float(i1)+float(i2)
	if ipf == 2:
		return float(i1)+float(i2)
	if ipf == 3:
		return float(i1)+float(i2)+1-.3
	if ipf == 4:
		return float(i1)+float(i2)+1-.3

def ipToOuts(ip):
	return int(round(float(ip))) * 9 + ipFrac(ip)

def HomeHandler(request):
	args = dict()
	c = {}
	
	getData(90973)
	getData(96560)
	getData(99345)
	getData(77704)
	getData(83443)
	
	u = User.objects.all()
		
	for user in u:
		user.totalpoints = 0
		user.totalpoints = Entry.objects.filter(uid__name=user.name).aggregate(Sum('points'))['points__sum']
		user.save()
		print user.totalpoints
	
	c['users'] = User.objects.all()
	
	
	message = render_to_response('index.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)
	
def StatsHandler(request):
	args = dict()
	c = {}
	
	u = User.objects.all()
	e = Entry.objects.all()
		

	for user in u:
		max_game = Entry.objects.filter(uid = user).aggregate(Max('gamenumber'))['gamenumber__max']
		for i in range(1,max_game):	
			try:
			    stats = UserStats.objects.get(uid=user,game=i)
			except ObjectDoesNotExist:
				stats = UserStats.objects.create(uid=user,abs=0,game=i,tbs=0,rbis=0,bbs=0,sbs=0,slug=0,runs=0,ips=0,phits=0,pbbs=0,ers=0,Ks=0,Ws=0,era=0)
			
			
			
				
			for p in PitcherEntry.objects.filter(entry__uid=user).filter(entry__gamenumber=i):
				if p.IP!=None:
					stats.ips = addIP(stats.ips,p.IP)
			stats.abs = PlayerEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('ABs'))['ABs__sum']
			stats.tbs = PlayerEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('TBs'))['TBs__sum']
			stats.runs = PlayerEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('RUNs'))['RUNs__sum']
			stats.rbis = PlayerEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('RBIs'))['RBIs__sum']
			stats.bbs = PlayerEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('BBs'))['BBs__sum']
			stats.sbs = PlayerEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('SBs'))['SBs__sum']
			stats.phits = PitcherEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('HITs'))['HITs__sum']
			stats.ers = PitcherEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('ERs'))['ERs__sum']
			stats.pbbs = PitcherEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('BBs'))['BBs__sum']
			stats.Ks = PitcherEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('Ks'))['Ks__sum']
			stats.Ws = PitcherEntry.objects.filter(entry__gamenumber=i).filter(entry__uid__name=user.name).aggregate(Sum('W'))['W__sum']
			if stats.ers > 0:
				stats.era = round(float(ipToOuts(stats.ips))/float(stats.ers)/9,3)
			else:
				stats.era = 0
			stats.slug = round(float(stats.tbs) /float(stats.abs),3)
		
			
			stats.save()			

	c['stats'] = UserStats.objects.all()

	message = render_to_response('stats.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

	
def PositionStatsHandler(request):
	params= request.GET
	id = params["id"]
	user = User.objects.get(espnid=id)
	
	
	positions = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]
	c={'C':[],'1B':[],'2B':[],'3B':[],'SS':[],'LF':[],'CF':[],'RF':[],'DH':[]}
	for i in range (0,9):
		e = PlayerEntry.objects.values('espnid').distinct().filter(entry__uid__name=user.name).filter(Position=positions[i])
		for es in e:	
			ABs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('ABs'))
			RUNs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('RUNs'))
			TBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('TBs'))
			RBIs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('RBIs'))
			BBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('BBs'))
			SBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('SBs'))
			PTs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=es['espnid']).aggregate(Sum('PTs'))
			pl = PlayerEntry.objects.filter(espnid=es['espnid'])
			name = ""
			
			for pp in pl:
				name = pp.name
			p = [name,positions[i],es['espnid'],ABs['ABs__sum'],RUNs['RUNs__sum'],TBs['TBs__sum'],RBIs['RBIs__sum'],BBs['BBs__sum'],SBs['SBs__sum'],PTs['PTs__sum']]
			
			c[positions[i]].append(p)
	#print c
	for posi in range (0,9):
		c[positions[posi]] = sorted(c[positions[posi]], key=lambda p: p[3], reverse=True)
	message = render_to_response('statspos.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)
	
	#for ent in user.entry_set.all():
		
			

def getData(id):
	ud = UserData(id)
	try:
		user = User.objects.get(espnid=id)    
	except ObjectDoesNotExist:
		ud = UserData(id)
		user = User.objects.get_or_create(name=ud['name'], espnid=id)
	user = User.objects.get(espnid=id)
	for i in range(1,10):
		try:
		    ent = Entry.objects.get(uid=user,gamenumber=i)
		except ObjectDoesNotExist:
			player = Baseball(id,i)
			ent = Entry.objects.create(uid=user,gamenumber=i,points=0)
			tpts=0
			for i in player:
				if 'TB' in i:
					pts = int(i['R']) + int(i['TB']) + int(i['RBI']) + int(i['BB']) + int(i['SB'])
					tpts += pts
					name = i['FN'] + " " + i['LN']
					
					pl = PlayerEntry.objects.create(name = name, Position = i['position'], espnid=i['id'], ABs=i['AB'], RUNs=i['R'], TBs=i['TB'], RBIs=i['RBI'], BBs=i['BB'], SBs=i['SB'],PTs=pts)
					#print pl
					ent.players.add(pl)
				if 'IP' in i:
					ipfrac = int(round((float(i['IP'])-round(float(i['IP'])))*10,0))
					ip = round(float(i['IP']))*3+ipfrac
					name = i['Team']
				
					pts = ip + int(i['K']) - int(i['H']) - (3*int(i['ER'])) - int(i['BB']) + (5*(int(i['W'])))
					tpts += pts
					#print i
					pi = PitcherEntry.objects.create(name = name, IP = i['IP'], espnid = i['id'], espnid2 = 0, HITs = i['H'], ERs = i['ER'], BBs = i['BB'], Ks = i['K'], W = i['W'], PTs = pts)
					ent.pitchers.add(pi)
			ent.points = tpts
			ent.save()

def UserData(id):
	s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
	sock = urllib.urlopen(s) 
	htmlSource = sock.read()
	sock.close() 
	
	soup = BeautifulSoup(htmlSource)
	title = soup.title
	
	ss = re.split('<title>ESPN - Baseball Challenge - |</title>', str(title))
	
	ss = filter(None, ss)
	
	x = soup.find("div", { "class" : "games-graph-data" })
	
	em= str(x)
	
	li = re.split('<em>|</em>',em)
	for i in li:
		for n in i:
			if n.isdigit():
				break;
			else:
				li.remove(i)
				break;
	userdata = {}
	userdata['name'] = ss[0]
	userdata['rank'] = li[2]
	userdata['pct'] = li[1]
	return userdata
	
	
def Baseball(id, day):

	#s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id) + "&spid=" + str(day)
	s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id) + "&spid=" + str(day)

	sock = urllib.urlopen(s) 
	htmlSource = sock.read()
	sock.close() 
	
	soup = BeautifulSoup(htmlSource)
	player = [{},{},{},{},{},{},{},{},{},{}]
	
	out = soup.findAll('td')

	i=17
	case=0
	pcount = 0
	
	stats = {}
	stats[5] = 'AB'
	stats[6] = 'R'
	stats[7] = 'TB'
	stats[8] = 'RBI'
	stats[9] = 'BB'
	stats[10] = 'SB'
	statsps = {}
	statsps[5] = 'IP'
	statsps[6] = 'H'
	statsps[7] = 'ER'
	statsps[8] = 'BB'
	statsps[9] = 'K'
	statsps[10] = 'W'
	playersdone = 0
	psactive = 0
	psdh = 0
	noopp=False
	while (i < len(out)):
		if playersdone==1:
			#print out[i]
			#print case
			#print out[i].string
			
			#if out[i].string == "PS":
			if i==151:
				psactive = 1
				case = 0
			if psactive == 1:

				#Pitching Staff, Pitcher id, DH Pitcher id, Team id
				if case == 2:
					s = str(out[i])
					fn = s.split('pFN\">')
					player[9]['Team'] = ""
					for ch in fn:
						for c in ch:
							if c == '<':
								break
							if c.isalpha() or c == ' ':
								player[9]['Team'] = player[9]['Team'] + c
					
					s = str(out[i])
					x = s.split('profile?playerId=')

					id = 0
					player[9]['id'] = ""
					player[9]['id2'] = ""
					if len(x)>1:
						for p in x[1]:
							if id == 0:
								if p.isdigit():
									player[9]['id'] = player[9]['id'] + p	
								else:
									if player[9]['id'] != "":
										id = 1
					if len(x)>2:
						for p in x[2]:
							if id ==1:
								if p.isdigit():
									player[9]['id2'] = player[9]['id2'] + p
					s = str(out[i])
					x = s.split('tid=\"')
					teamid = 0
					player[9]['teamid'] = ""
					for p in x[1]:
						if teamid == 0:
							if p.isdigit():
								player[9]['teamid'] = player[9]['teamid'] + p	
							else:
								if player[9]['teamid'] != "":
									teamid = 1

				#Location, Opponent Team, Opponent Pitcher
				if case == 3:
					if "@" in s:
						player[9]['loc'] = "Away"
					else:
						player[9]['loc'] = "Home"
					s = str(out[i])
					if "http" in s:
						s = str(out[i])
						f = s.split('teamId=')
						player[9]['oid'] = ""
						oid = 0
						for p in f[1]:
							if oid == 0:
								if p.isdigit():
									player[9]['oid'] = player[9]['oid'] + p	
								else:
									if player[9]['oid'] != "":
										oid = 1
						s = str(out[i])
						pit = s.split(' - ')
						player[9]['opppit'] = ""
						for ch in pit[1]:
							if ch == '\"':
								break;
							if ch.isalpha():
								player[9]['opppit'] = player[9]['opppit'] + ch

				#If off day fill in pitcher ids as 0
				if case == 4:
					if out[i].string == '--':
						noopp = True
						player[9]['id']=0
						player[9]['id2']=0			

				#IP, H, ER, BB, K
				if case == 5:
					if noopp:
						player[9][statsps[case]] = 0
					else:
						if out[i].string == None:
							s = str(out[i])
							x = s.split('>')
							ip1 = ""
							ip2 = ""
							print x
							for n in x:
								for c in n:
									if c.isdigit() or c == '.':
										if psdh == 1:
											ip2 = ip2 + c
										else:
											ip1 = ip1 + c
									
									if c == '<':
										if ip1 != "":
											psdh = 1
										break
							player[9][statsps[case]] = addIP(ip1,ip2)
						else:
							player[9][statsps[case]] = out[i].string
				if case == 6 or case == 7 or case == 8 or case == 9 or case == 10:
					if noopp:
						player[9][statsps[case]] = 0
					else:
						if out[i].string == None:
							s = str(out[i])
							x = s.split('>')
							#print x
							for n in x:
								for c in n:
									if c.isdigit():
										if statsps[case] in player[9]:
											player[9][statsps[case]] = int(player[9][statsps[case]])+int(c)
										else:
											player[9][statsps[case]] = int(c)
									if c == '<':
										break
						else:
							player[9][statsps[case]] = out[i].string
				if case == 12:
					s = str(out[i])
					sal = s.split('<nobr>')
					g = 0
					p = sal[1][g]
					player[9]['salary'] = ""
					while p.isdigit() or p == '.':
						player[9]['salary'] = player[9]['salary']+p
						g+=1
						p=sal[1][g]
				if case == 13:	
					psactive = 0
					#print ps
					#print player
					#print "break"	
				case +=1
			i+=1
		else:
			#print out[i]
			#print case
			#print out[i].string
			s = str(out[i])
			if "player_eid" in s:
				x = s.split('player_eid=\"')
				for h in x:
					g = 0
					p = h[g]
					player[pcount]['id'] = ""
					while p.isdigit():
						player[pcount]['id'] = player[pcount]['id'] + p
						g+=1
						p=h[g]
			if "teamId" in s:
				s = str(out[i])
				f = s.split('teamId=')
				player[pcount]['oid'] = ""
				oid = 0
				for p in f[1]:
					if oid == 0:
						if p.isdigit():
							player[pcount]['oid'] = player[pcount]['oid'] + p	
						else:
							if player[pcount]['oid'] != "":
								oid = 1
				s = str(out[i])
				pit = s.split(' - ')
				player[pcount]['opppit'] = ""
				#print pit[1]
				for ch in pit[1]:
					if ch == '\"':
						break;
					if ch.isalpha():
						player[pcount]['opppit'] = player[pcount]['opppit'] + ch
							#print player[9]['opp']
			if case == 0:
				player[pcount]['position'] = out[i].string
			if case == 2:
				s = str(out[i])
				f = s.split('pFN\">')
				player[pcount]['FN'] = ""
				for n in f:
					for c in n:
						#print c
						if c == '<':
							break
						if c.isalpha():
							player[pcount]['FN'] = player[pcount]['FN'] + c
			if case == 2:
				s = str(out[i])
				f = s.split('pLN\">')
				player[pcount]['LN'] = ""
				for n in f:
					for c in n:
						if c == '<':
							break
						if c.isalpha():
							player[pcount]['LN'] = player[pcount]['LN'] + c
			if case == 5 or case == 6 or case == 7 or case == 8 or case == 9 or case ==10:
				if out[i].string == None:
					x = s.split('>')
					for n in x:
						for c in n:
							if c.isdigit():
								if stats[case] in player[pcount]:
									player[pcount][stats[case]] = int(player[pcount][stats[case]])+int(c)
								else:
									player[pcount][stats[case]] = int(c)
							if c == '<':
								break
				else:
					player[pcount][stats[case]] = out[i].string
			if case == 12:
				s = str(out[i])
				sal = s.split('<nobr>')
				g = 0
				p = sal[1][g]
				player[pcount]['salary'] = ""
				while p.isdigit() or p == '.':
					player[pcount]['salary'] = player[pcount]['salary']+p
					g+=1
					p=sal[1][g]
				case =-1
				pcount +=1
				if pcount == 9:
					playersdone=1
			i+=1
			case+=1
			#print case
	return player
