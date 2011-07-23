
from django.template import Context, loader, RequestContext
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render_to_response
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.utils import simplejson
from django.db.models import Q, Max, Sum, Avg
from datetime import datetime
from bbcstats.bbc.models import *
from django.core.exceptions import ObjectDoesNotExist
import os.path
import teams
import re
import urllib, urllib2
from datetime import date
from BeautifulSoup import *
import lxml.html
from lxml import html
from lxml.etree import tostring

def ipFrac(i):
	if i == None:
		return 0
	return int(round((float(i)-round(float(i)))*10,0))


def addIP(i1,i2):
	if i1 == None:
		return i2
	if i2 == None:
		return i1
	ipf1 = ipFrac(i1)
	ipf2 = ipFrac(i2)
	#print ipf1
	#print ipf2
	ipf = ipf1+ipf2
	#print i1
	#print i2
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

def totalStatsUpdater(user,maxgame):
	try:
	    tot = TotalStats.objects.get(uid=user)
	except ObjectDoesNotExist:
		tot = TotalStats.objects.create(uid=user,abs=0,tbs=0,rbis=0,bbs=0,sbs=0,slug=0,runs=0,ips=0,phits=0,pbbs=0,ers=0,Ks=0,Ws=0,era=0)
	ustat = UserStats.objects.filter(uid=user)
	
	tot.abs = ustat.all().aggregate(Sum('abs'))['abs__sum']
	tot.tbs = ustat.all().aggregate(Sum('tbs'))['tbs__sum']
	tot.rbis = ustat.all().aggregate(Sum('rbis'))['rbis__sum']
	tot.bbs = ustat.all().aggregate(Sum('bbs'))['bbs__sum']
	tot.runs = ustat.all().aggregate(Sum('runs'))['runs__sum']
	for p in ustat.all():
		tot.ips = addIP(tot.ips,p.ips)
	tot.ips = ustat.all().aggregate(Sum('ips'))['ips__sum']
	tot.phits = ustat.all().aggregate(Sum('phits'))['phits__sum']
	tot.pbbs = ustat.all().aggregate(Sum('pbbs'))['pbbs__sum']
	tot.ers = ustat.all().aggregate(Sum('ers'))['ers__sum']
	tot.Ks = ustat.all().aggregate(Sum('Ks'))['Ks__sum']
	tot.Ws = ustat.all().aggregate(Sum('Ws'))['Ws__sum']
	
	if tot.abs > 0:
		tot.slug = float(tot.tbs) /float(tot.abs)
		tot.ptsabs = float(tot.tbs+tot.runs+tot.rbis+tot.bbs+tot.sbs)/float(tot.abs)
	else:
		tot.slug = 0
		tot.ptsabs = 0
	if tot.ers > 0:
		tot.era = float(ipToOuts(tot.ips))/float(tot.ers)/9
	else:
		tot.era = 0
	
	tot.points = user.totalpoints
	tot.maxgame = maxgame
	tot.save()

def totalStatsTeamUpdater(user,teamid,maxgame):
	try:
		tot = TotalTeamStats.objects.get(uid=user,teamid=teamid)
		if tot.maxgame >= maxgame:
			return
	except ObjectDoesNotExist:
		tot = TotalTeamStats.objects.create(uid=user,teamid=teamid,teamname=teams.team[teamid],abs=0,tbs=0,rbis=0,bbs=0,sbs=0,slug=0,runs=0,ips=0,phits=0,pbbs=0,ers=0,Ks=0,Ws=0,era=0)
		
	pla = PlayerEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
	
	tot.abs = pla.all().aggregate(Sum('abs'))['abs__sum']
	tot.tbs = pla.all().aggregate(Sum('tbs'))['tbs__sum']
	tot.rbis = pla.all().aggregate(Sum('rbis'))['rbis__sum']
	tot.bbs = pla.all().aggregate(Sum('bbs'))['bbs__sum']
	tot.runs = pla.all().aggregate(Sum('runs'))['runs__sum']
	
	pit = PitcherEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
	
	for p in pit.all():
		tot.ips = addIP(tot.ips,p.ip)
		
	tot.phits = pit.all().aggregate(Sum('hits'))['hits__sum']
	tot.pbbs = pit.all().aggregate(Sum('bbs'))['bbs__sum']
	tot.ers = pit.all().aggregate(Sum('ers'))['ers__sum']
	tot.Ks = pit.all().aggregate(Sum('ks'))['ks__sum']
	tot.Ws = pit.all().aggregate(Sum('w'))['w__sum']
	
	if tot.abs > 0:
		tot.slug = float(tot.tbs) /float(tot.abs)
		tot.ptsabs = float(tot.tbs+tot.runs+tot.rbis+tot.bbs+tot.sbs)/float(tot.abs)
	else:
		tot.slug = 0
		tot.ptsabs = 0
	if tot.ers > 0:
		tot.era = float(ipToOuts(tot.ips))/float(tot.ers)/9
	else:
		tot.era = 0
		
#	tot.points = user.totalpoints
	tot.maxgame= maxgame
	tot.save()
	#print tot

def HomeHandler(request):
	args = dict()
	
	params= request.GET
	
	c = {}
	getData(90973)
	getData(96560)
	getData(99345)
	getData(77704)
	getData(83443)
	getData(523)
	getData(1652)

	u = User.objects.all()
		
	for user in u:
		user.totalpoints = 0
		user.totalpoints = Entry.objects.filter(uid__name=user.name).aggregate(Sum('points'))['points__sum']
		user.save()
		#print user.totalpoints
	
	c['users'] = User.objects.all()
	
	message = render_to_response('index.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

	
def StatsHandler(request):
	args = dict()
	c = {}
	
	u = User.objects.all()
	for user in u:
		max_game = Entry.objects.filter(uid = user).aggregate(Max('gamenumber'))['gamenumber__max']
		#print str(max_game) + "max "
		for i in range(1,max_game+1):	
			#print i
			try:
				stats = UserStats.objects.get(uid=user,game=i)
			except ObjectDoesNotExist:
				stats = UserStats.objects.create(uid=user,abs=0,game=i,tbs=0,rbis=0,bbs=0,sbs=0,slug=0,runs=0,ips=0,phits=0,pbbs=0,ers=0,Ks=0,Ws=0,era=0)
			#Might need in future if change to doubleheader system
			#for p in PitcherEntry.objects.filter(entry__uid=user).filter(entry__gamenumber=i):
				#stats.ips = p.IP
				e = Entry.objects.filter(uid=user).filter(gamenumber=i)
				for t in e:
					stats.abs = t.players.all().aggregate(Sum('abs'))['abs__sum']
					stats.tbs = t.players.all().aggregate(Sum('tbs'))['tbs__sum']
					stats.runs = t.players.all().aggregate(Sum('runs'))['runs__sum']
					stats.rbis = t.players.all().aggregate(Sum('rbis'))['rbis__sum']
					stats.bbs = t.players.all().aggregate(Sum('bbs'))['bbs__sum']
					stats.sbs = t.players.all().aggregate(Sum('sbs'))['sbs__sum']
					stats.ips = 0
					for p in t.pitchers.all():
						stats.ips = addIP(stats.ips,p.ip)
					stats.ips = t.pitchers.all().aggregate(Sum('ip'))['ip__sum']
					stats.phits = t.pitchers.all().aggregate(Sum('hits'))['hits__sum']
					stats.pbbs = t.pitchers.all().aggregate(Sum('bbs'))['bbs__sum']
					stats.ers = t.pitchers.all().aggregate(Sum('ers'))['ers__sum']
					stats.Ks = t.pitchers.all().aggregate(Sum('ks'))['ks__sum']
					stats.Ws = t.pitchers.all().aggregate(Sum('w'))['w__sum']
					if stats.ers > 0:
						stats.era = float(ipToOuts(stats.ips))/float(stats.ers)/9
					else:
						stats.era = 0
					if stats.abs > 0:
						stats.slug = float(stats.tbs) /float(stats.abs)
						stats.ptsabs = float(stats.tbs+stats.runs+stats.rbis+stats.bbs+stats.sbs)/float(stats.abs)
					else:
						stats.slug = 0
						stats.ptsabs = 0
					if stats.runs > stats.ers:
						stats.runwin = 1
					else:
						if stats.runs == stats.ers:
							stats.runwin = 0
						else:
							stats.runwin = -1
					if stats.rbis > stats.ers:
						stats.rbiwin = 1
					else:
						if stats.rbis == stats.ers:
							stats.rbiwin = 0
						else:
							stats.rbiwin = -1
					
					stats.save()
		for i in range(1,30):
			totalStatsTeamUpdater(user,i,max_game)
		print "stats done"
		print user.name
		totalStatsUpdater(user,max_game)
		
	u = User.objects.all()
	#for user in u:
	#	sum = UserStats.objects.filter(uid=user).aggregate(Sum)
	print "stats done"
	c['stats'] = UserStats.objects.all()
	
	message = render_to_response('stats.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

	
def PositionStatsHandler(request):
	params= request.GET
	id = params["id"]
	user = User.objects.get(espnid=id)
	
	positions = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]
	positionstr = ["Catcher", "First Base", "Second Base", "Third Base", "Shortstop", "Left Field", "Center Field", "Right Field", "Designated Hitter"]
	c={'pos':[], 'C':[],'1B':[],'2B':[],'3B':[],'SS':[],'LF':[],'CF':[],'RF':[],'DH':[],'totals':{},'sums':[],'P':[]}
	c['sums'] = TotalStats.objects.get(uid=user)
	c['pos']=positions
	for i in range (0,9):
		e = PlayerEntry.objects.values('espnid').distinct().filter(entry__uid__name=user.name).filter(Position=positions[i])
		for es in e:
			espnid = es['espnid']	
			ABs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('ABs'))['ABs__sum']
			RUNs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('RUNs'))['RUNs__sum']
			TBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('TBs'))['TBs__sum']
			RBIs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('RBIs'))['RBIs__sum']
			BBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('BBs'))['BBs__sum']
			SBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('SBs'))['SBs__sum']
			PTs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('PTs'))['PTs__sum']
			salary = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Avg('salary'))['salary__avg']
			
			ptspersalary = round(float(PTs)/salary,3)
			
			pl = PlayerEntry.objects.filter(espnid=espnid)
			
			name = ""
			
			for pp in pl:
				name = pp.name
			p = [name,positions[i],espnid,ABs,RUNs,TBs,RBIs,BBs,SBs,PTs, salary,ptspersalary]
			
			c[positions[i]].append(p)
	#print c
	pe = PitcherEntry.objects.values('espnid').distinct().filter(entry__uid__name=user.name)
	for es in pe:
		espnid = es['espnid']
		ps = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid)
		ip = 0
		name = ""
		for p in ps:
			ip = addIP(p.IP,ip)
			name = p.name
		hits = ABs = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('HITs'))['HITs__sum']
		ers = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('ERs'))['ERs__sum']
		bbs = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('BBs'))['BBs__sum']
		ks = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('Ks'))['Ks__sum']
		w = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('W'))['W__sum']
		pts = PitcherEntry.objects.filter(entry__uid__name=user.name).filter(espnid=espnid).aggregate(Sum('PTs'))['PTs__sum']
		pi = [name,ip,hits,ers,bbs,ks,w,pts]
		c['P'].append(pi)
		
	for i in range(0,9):
		c['totals'][positions[i]] = []
		ABs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('ABs'))['ABs__sum']
		RUNs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('RUNs'))['RUNs__sum']
		TBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('TBs'))['TBs__sum']
		RBIs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('RBIs'))['RBIs__sum']
		BBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('BBs'))['BBs__sum']
		SBs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('SBs'))['SBs__sum']
		PTs = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Sum('PTs'))['PTs__sum']
		salary = PlayerEntry.objects.filter(entry__uid__name=user.name).filter(Position=positions[i]).aggregate(Avg('salary'))['salary__avg']
		ptspersalary = round(float(PTs)/salary,3)
		p = [positionstr[i],positions[i],"",ABs,RUNs,TBs,RBIs,BBs,SBs,PTs,salary,ptspersalary ]
		c['totals'][positions[i]].append(p)
	#print c['totals']
	c['ptotals'] = TotalStats.objects.get(uid=user)
	for posi in range (0,9):
		c[positions[posi]] = sorted(c[positions[posi]], key=lambda p: p[3], reverse=True)
	message = render_to_response('statspos.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)
	
	#for ent in user.entry_set.all():

		
def viewRanks(request):
	u = User.objects.all()
	for user in u:
		d = UserData(user.espnid)
		stat = UserRank.objects.get_or_create(uid = user, rank = d['rank'], pct = d['pct'],date=date.today())
	st = UserRank.objects.all()
	st = st.order_by('-uid')
	for i in st:
		print i.uid.name
		print i.rank
		print i.date
	return HttpResponse()	

#def computeLog(request):
#u = User.objects.all()
#for user in u:
#	ent = Entry.objects.filter(uid=user)
#	for e in ent:
#		prev = []
#		if e.gamenumber == 1:
#			for p in e.players.all():
					
				
			

def getData(id):
	try:
		user = User.objects.get(espnid=id)    
	except ObjectDoesNotExist:
		ud = UserData(id)
		user = User.objects.get_or_create(name=ud['name'], espnid=id)
	user = User.objects.get(espnid=id)
	for i in range(1,111):
		try:
		    ent = Entry.objects.get(uid=user,gamenumber=i)
		except ObjectDoesNotExist:
			player = parser(id,i)
			ent = Entry.objects.create(uid=user,gamenumber=i,points=0)
			tpts=0
			for i in player:
				if 'TB' in i:
					pts = int(i['R']) + int(i['TB']) + int(i['RBI']) + int(i['BB']) + int(i['SB'])
					tpts += pts
					name = i['FN'] + " " + i['LN']
					pl,created = PlayerEntry.objects.get_or_create(name = name, pos = i['pos'], bbcid=i['id'],doubleheader = i['dh'], espnid =i['espnid'], abs=i['AB'], runs=i['R'], tbs=i['TB'], rbis=i['RBI'], bbs=i['BB'], sbs=i['SB'],pts=pts, salary =i['salary'],teamid =i['teamid'],teamname=teams.team[int(i['teamid'])])
					ent.players.add(pl)
				if 'IP' in i:
					ipfrac = int(round((float(i['IP'])-round(float(i['IP'])))*10,0))
					ip = round(float(i['IP']))*3+ipfrac
					name = teams.team[int(i['teamid'])]
				
					pts = ip + int(i['K']) - int(i['H']) - (3*int(i['ER'])) - int(i['BB']) + (5*(int(i['W'])))
					tpts += pts
					#print i
					pi,created = PitcherEntry.objects.get_or_create(name = name, ip = i['IP'], espnid = i['id'], espnid2 = i['id2'], doubleheader = i['dh'], hits = i['H'], ers = i['ER'], bbs = i['BB'], ks = i['K'], w = i['W'], pts = pts, salary =i['salary'], teamid =i['teamid'], teamname=teams.team[int(i['teamid'])])
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

def viewTop100Lineup(request):
	c = {}
	try:
		top = Top100Lineup.objects.get(date=date.today())
	except ObjectDoesNotExist:
		top = Top100Lineup.objects.create(date=date.today())
		leaders = getLeaders()
		for i in range(1,len(leaders)+1):
			l = getLineup(leaders[i])
			line = Lineup.objects.create(name="")
			for i in l:
				print i['position']
				if i['position']=="C":
					line.catcher = i['FN'] + " " + i['LN']
					print i['FN'] + " " + i['LN']
				if i['position']=="1B":
					line.firstbase = i['FN'] + " " + i['LN']
				if i['position']=="2B":
					line.secondbase = i['FN'] + " " + i['LN']
				if i['position']=="3B":
					line.thirdbase = i['FN'] + " " + i['LN']
				if i['position']=="SS":
					line.shortstop = i['FN'] + " " + i['LN']
				if i['position']=="LF":
					line.leftfield = i['FN'] + " " + i['LN']
				if i['position']=="CF":
					line.centerfield = i['FN'] + " " + i['LN']
				if i['position']=="RF":
					line.rightfield = i['FN'] + " " + i['LN']
				if i['position']=="DH":
					line.dh = i['FN'] + " " + i['LN']
				if i['position']=="PS":
					line.ps = i['Team']
				line.save()
			top.top100.add(line)
			top.save()
	c['lineup'] = Top100Lineup.objects.get(date=date.today()).top100.all()
	
	message = render_to_response('top100.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

		
	
def getLeaders():
	req = urllib2.Request('http://games.espn.go.com/baseball-challenge/en/leaderboard?segment=-1&scoringSystemID=2&periodStart=15&univ=0')
	response = urllib2.urlopen(req)
	htmlSource = response.read()
	soup = BeautifulSoup(htmlSource)
	
	odd = soup.findAll("tr", {"class" : "oddrow"})
	even = soup.findAll("tr", {"class" : "evenrow"})
	
	leader = {}
	for i in range (0,50):
		s = str(odd[i])
		x = s.split('entry?entryID=')
		id = ""
		for ch in x[1]:
			if ch == '\"':
				break;
			if ch.isdigit():
				
				id = id + ch
		leader[i*2+1] = id
		getData(int(id))
		s = str(even[i])
		x = s.split('entry?entryID=')
		id2 = ""
		for ch in x[1]:
			if ch == '\"':
				break;
			if ch.isdigit():
				id2 = id2 + ch
		leader[i*2+2] = id2
		getData(int(id2))
	return leader

def getLineup(id):
	file = "/Users/Jason/bbcdata/" + str(id) + str(date.today())
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id)
		sock = urllib.urlopen(s) 
		htmlSource = sock.read()
		sock.close() 
		source = open(file,"w")
		source.writelines(htmlSource)
		source.close()
		
	infile = open(file,"r")
	html = infile.read()
	
	soup = BeautifulSoup(html)
	player = [{},{},{},{},{},{},{},{},{},{}]
	
	out = soup.findAll('td')
	i=17
	case=0
	pcount = 0
	
	playersdone = 0
	psactive = 0
	psdh = 0
	noopp=False
	for i in range(17,len(out)+1):
		if playersdone==1:
			if i==151:
				psactive = 1
				case = 0
			if psactive == 1:
				#Pitching Staff, Pitcher id, DH Pitcher id, Team id
				if case == 2:
					player[9]['position']="PS"
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
						if len(pit)>1:
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
				case +=1
			#i+=1
		else:
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
				if len(pit) > 1:
					for ch in pit[1]:
						if ch == '\"':
							break;
						if ch.isalpha():
							player[pcount]['opppit'] = player[pcount]['opppit'] + ch
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
				x = s.split('tid=\"')
				teamid = 0
				player[pcount]['teamid'] = ""
				for p in x[1]:
					if teamid == 0:
						if p.isdigit():
							player[pcount]['teamid'] = player[pcount]['teamid'] + p	
						else:
							if player[pcount]['teamid'] != "":
								teamid = 1
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
			case+=1
	return player

def Baseball(id,day):
	file = "/Users/Jason/bbcdata/" + str(id) + "&spid=" + str(day)
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id) + "&spid=" + str(day)
		sock = urllib.urlopen(s) 
		htmlSource = sock.read()
		sock.close() 
		source = open(file,"w")
		source.writelines(htmlSource)
		source.close()
		
	infile = open(file,"r")
	html = infile.read()
	#s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id) + "&spid=" + str(day)
	soup = BeautifulSoup(html)
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
	for i in range(17,len(out)+1):
		if playersdone==1:
			
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
						if len(pit)>1:
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
				case +=1
			#i+=1
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
				if len(pit) > 1:
					for ch in pit[1]:
						if ch == '\"':
							break;
						if ch.isalpha():
							player[pcount]['opppit'] = player[pcount]['opppit'] + ch
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
				x = s.split('tid=\"')
				teamid = 0
				player[pcount]['teamid'] = ""
				for p in x[1]:
					if teamid == 0:
						if p.isdigit():
							player[pcount]['teamid'] = player[pcount]['teamid'] + p	
						else:
							if player[pcount]['teamid'] != "":
								teamid = 1
								
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
			case+=1
	return player


def parser(id,day):
	#t = []
	file = "/Users/Jason/bbcdata/" + str(id) + "&spid=" + str(day)
	#t.append(time.time())#####
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id) + "&spid=" + str(day)
		sock = urllib.urlopen(s) 
		htmlSource = sock.read()
		sock.close() 
		source = open(file,"w")
		source.writelines(htmlSource)
		source.close()

	infile = open(file,"r")
	htmlsource = infile.read()


	#t.append(time.time())######
	root = html.fromstring(htmlsource)

	#t.append(time.time())######	
	data = root.cssselect('tbody')

	#t.append(time.time())######

	pl = data[0].cssselect('tr')	

	player = [{},{},{},{},{},{},{},{},{},{}]
	stat={5:"AB",6:"R",7:"TB",8:"RBI",9:"BB",10:"SB"}
	i = 0
	#t.append(time.time())##########
	for s in pl:
		l1 = s.cssselect("td")
		player[i]['pos'] = l1[0].text
		l12 = tostring(l1[2])
		player[i]['FN'] = l12.split('pFN\">')[1].split('<')[0]
		player[i]['LN'] = l12.split('pLN\">')[1].split('<')[0]
		player[i]['id'] = l12.split('player_id=\"')[1].split('\"')[0]
		player[i]['espnid'] = l12.split('player_eid=\"')[1].split('\"')[0]
		player[i]['teamid'] = l12.split('tid=\"')[1].split('\"')[0]
		player[i]['salary'] = tostring(l1[12]).strip('<>td  = clasnobr///"')

		player[i]['dh'] = False

		if(l1[3].text != "--"):

			player[i]['oppteamid'] = tostring(l1[3]).split('teamId=')[1].split('\"')[0]
			if l1[5].text == None:
				player[i]['dh'] = True
				for j in range(5,11):
					s1 = l1[j].cssselect('span')[0]
					s2 = l1[j].cssselect('span')[1]
					player[i][stat[j]] = int(s1.text)+int(s2.text)
			else:
				for j in range(5,11):
					player[i][stat[j]] = l1[j].text
		#else:
			#print "noop"
		#player[i]['R'] = l1[6].text
		#player[i]['TB'] = l1[7].text
		#player[i]['RBI'] = l1[8].text
		#player[i]['BB'] = l1[9].text
		#player[i]['SB'] = l1[10].text
		if "@" in str(l1[3]):
			player[i]['loc'] = "Away"
		else:
			player[i]['loc'] = "Home"

		l=0
		i+=1

	#p = data[1].cssselect('tr')[0].cssselect("td")
#	t.append(time.time())###########
	p = data[1].cssselect("td")
	#for d in range(1,4):
#		print d
#		print tostring(p[d])

	player[9]['pos'] = "PS"
	p2 = tostring(p[2])
	player[9]['id'] = 0
	player[9]['id2'] = 0
	player[9]['teamid'] = p2.split('tid=\"')[1].split('\"')[0]
	player[9]['dh'] = False
	if p[3].text != "--":
		if "\"roster-plyr\"" in p2:
			player[9]['id'] = p2.split('playerId=')[1].split('\"')[0]
		player[9]['oppteamid'] = tostring(p[3]).split('teamId=')[1].split('\"')[0]
		statps={5:"IP",6:"H",7:"ER",8:"BB",9:"K",10:"W"}
		if p[5].text == None:
			player[9]['id2'] = p2.split('playerId=')[2].split('\"')[0]
			player[9]['dh'] = True
			for j in range(5,11):
				s1 = p[j].cssselect('span')[0]
				s2 = p[j].cssselect('span')[1]
				player[9][statps[j]] = addIP(s1.text,s2.text)
		else:
			for j in range(5,11):
				player[9][statps[j]] = p[j].text

	player[9]['salary'] = tostring(p[12]).strip('<>td  = clasnobr///"')

#	t.append(time.time())
#	t.append(time.time())
#	for i in range (0,len(t)-1):
#		print i
#		print t[i+1]-t[i]
	return player