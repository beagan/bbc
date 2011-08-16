
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
from django.core.exceptions import ObjectDoesNotExist

import sqlite3


from datetime import datetime
from bbcstats.bbc.models import *
from datetime import date
from BeautifulSoup import *
from lxml import html
from lxml.etree import tostring
from StringIO import StringIO

import os.path
import re
import urllib, urllib2
import lxml.html
import gzip
import teams
import httplib2
import time

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
	return int(round(float(ip))) * 3 + ipFrac(ip)

def totalStatsUpdater(user,maxgame):
	try:
		tot = TotalStats.objects.get(uid=user)
		if tot.maxgame >= maxgame:
			return
	except ObjectDoesNotExist:
		tot = TotalStats.objects.create(uid=user)
	
	entry = Entry.objects.filter(uid=user)
	
	agg = entry.all().aggregate(Sum('abs'),Sum('tbs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('runs'),Sum('phits'),Sum('pbbs'),Sum('ers'),Sum('ks'),Sum('ws'),Sum('rbiwin'),Sum('rbitie'),Sum('rbiloss'),Sum('runwin'),Sum('runtie'),Sum('runloss'),Sum('points'))
	tot.abs = agg['abs__sum']
	tot.tbs = agg['tbs__sum']
	tot.rbis = agg['rbis__sum']
	tot.bbs = agg['bbs__sum']
	tot.sbs = agg['sbs__sum']
	tot.runs = agg['runs__sum']
	for p in entry.all():
		tot.ips = addIP(tot.ips,p.ips)
	tot.phits = agg['phits__sum']
	tot.pbbs = agg['pbbs__sum']
	tot.ers = agg['ers__sum']
	tot.ks = agg['ks__sum']
	tot.ws = agg['ws__sum']
	print user.name
	
	tot.runwin = agg['runwin__sum']
	tot.runtie = agg['runtie__sum']
	tot.runloss = agg['runloss__sum']
	
		
	tot.rbiwin = agg['rbiwin__sum']
	tot.rbitie = agg['rbitie__sum']
	tot.rbiloss = agg['rbiloss__sum']
			
	if tot.abs > 0:
		tot.slug = float(agg['tbs__sum']) /float(agg['abs__sum'])
		tot.ptsabs = float(agg['tbs__sum']+agg['runs__sum']+agg['rbis__sum']+agg['bbs__sum']+agg['sbs__sum'])/float(agg['abs__sum'])
	else:
		tot.slug = 0
		tot.ptsabs = 0
	if tot.ers > 0:
		tot.era = float(agg['ers__sum']*9)/(float(ipToOuts(tot.ips))/3)
	else:
		tot.era = 0
	pts = agg['points__sum']
	tot.points = pts
	#user.totalpoints = pts
	#user.save()
	tot.maxgame = maxgame
	tot.save()

def totalStatsTeamUpdater(user,teamid,maxgame):
	try:
		tot = TotalTeamStats.objects.get(uid=user,teamid=teamid)
		if tot.maxgame >= maxgame:
			return
	except ObjectDoesNotExist:
		tot = TotalTeamStats.objects.create(uid=user,teamid=teamid)
		
	pla = PlayerEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
	agg = pla.all().aggregate(Sum('abs'),Sum('tbs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('runs'))
	tot.abs = agg['abs__sum']
	tot.tbs = agg['tbs__sum']
	tot.rbis = agg['rbis__sum']
	tot.bbs = agg['bbs__sum']
	tot.sbs = agg['sbs__sum']
	tot.runs = agg['runs__sum']
	
	pit = PitcherEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
	
	for p in pit.all():
		tot.ips = addIP(tot.ips,p.ip)
	aggp = pit.all().aggregate(Sum('hits'),Sum('bbs'),Sum('ers'),Sum('ks'),Sum('w'))
	tot.phits = aggp['hits__sum']
	tot.pbbs = aggp['bbs__sum']
	tot.ers = aggp['ers__sum']
	tot.ks = aggp['ks__sum']
	tot.ws = aggp['w__sum']
	
	if tot.abs > 0:
		tot.slug = float(tot.tbs) /float(tot.abs)
		tot.ptsabs = float(tot.tbs+tot.runs+tot.rbis+tot.bbs+tot.sbs)/float(tot.abs)
	else:
		tot.slug = 0
		tot.ptsabs = 0
	if tot.ers > 0:
		tot.era = float(tot.ers*9)/(float(ipToOuts(tot.ips))/3)
	else:
		tot.era = 0
		
	tot.points = user.totalpoints
	tot.maxgame= maxgame
	tot.save()
	#print tot

def HomeHandler(request):
	args = dict()
	
	params= request.GET
	
#	today = date.today()
#	start = date(today.year, 3 ,31)
	#getData(90973)
	
	c = {}
	u = User.objects.all()
		
	#for user in u:
	#	getData(user.espnid)
	#	totalStatsUpdater(user,15)
	#	try:
	#		tpts = TotalStats.objects.get(uid=user)
	#	except:
	#		user.totalpoints = 0
	#	else:
	#		print tpts.points
	#		user.totalpoints = tpts.points
	#	user.save()
		#print user.totalpoints
	q= User.objects.all().order_by('totalpoints').reverse()
	
	paginator = Paginator(q, 10)
	try:
		page = int(request.GET.get('page', '1'))
	except ValueError:
		page = 1
    # If page request (9999) is out of range, deliver last page of results.
	try:
		qs = paginator.page(page)
	except (EmptyPage, InvalidPage):
		qs = paginator.page(paginator.num_pages)
	#getAllUsers()
	getDataNew(90973)
	c['users'] = qs
	
	message = render_to_response('index.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

	
def StatsHandler(request):
	args = dict()
	c = {}
	
	u = User.objects.all()
	for user in u:
		t1 = time.time()
		max_game = Entry.objects.filter(uid=user).aggregate(Max('gamenumber'))['gamenumber__max']
		if (((max_game != max_game_stat)) or max_game_stat == None) and max_game != None:
			for i in range(1,max_game+1):	
				#print i
				for i in range(1,30):
					totalStatsTeamUpdater(user,i,max_game)
		#print "stats done"
		#print user.name
			totalStatsUpdater(user,max_game)
			t2 = time.time()
			print t2-t1
	u = User.objects.all()
	#for user in u:
	#	sum = UserStats.objects.filter(uid=user).aggregate(Sum)
	print "stats done"
	c['stats'] = TotalStats.objects.all()
	
	message = render_to_response('stats.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)


def PositionStatsHandler(request):
	params= request.GET
	id = params["id"]
	t1 = time.time()
	user = User.objects.get(espnid=id)
	
	positions = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]
	positionstr = ["Catcher", "First Base", "Second Base", "Third Base", "Shortstop", "Left Field", "Center Field", "Right Field", "Designated Hitter"]
	c={'pos':[], 'C':[],'1B':[],'2B':[],'3B':[],'SS':[],'LF':[],'CF':[],'RF':[],'DH':[],'totals':{},'sums':[],'P':[]}
	#c['sums'] = TotalStats.objects.get(uid=user)
	c['pos']=positions
	for i in range (0,9):
		pe = PlayerEntry.objects.filter(entry__uid=user)
		e = pe.values_list('espnid', flat=True).distinct().filter(pos=positions[i])
		for es in e:
			
			espnid = es
			
			peespn = pe.filter(espnid=espnid)
			#print peespn.count()
			
			#t3 = time.time()
			peagg = peespn.aggregate(Sum('abs'))
			#t4 = time.time()
			#print str(t4-t3) + " values"
			#t1 = time.time()
			peagg = peespn.aggregate(Sum('abs'),Sum('tbs'),Sum('runs'),Sum('tbs'),Sum('runs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('pts'),Avg('salary'))
			#t2 = time.time()
			#print str(t2-t1) + " large"
			#t1= time.time()
			#peaggs = peespn.aggregate(Avg('salary'))	
			
			#t2 = time.time()
			#print str(t2-t1) + " avg	"
			
			ABs = peagg['abs__sum']
			RUNs = peagg['runs__sum']
			TBs = peagg['tbs__sum']
			RBIs = peagg['rbis__sum']
			BBs = peagg['bbs__sum']
			SBs = peagg['sbs__sum']
			PTs = peagg['pts__sum']
			salary = peagg['salary__avg']
			ptspersalary = round(float(PTs)/salary,3)
			
			pl = PlayerEntry.objects.filter(espnid=espnid)
			
			name = ""
			for pp in pl:
				name = pp.name
				break
			p = [name,positions[i],espnid,ABs,RUNs,TBs,RBIs,BBs,SBs,PTs, salary,ptspersalary]
			c[positions[i]].append(p)
	#print c
	pe = PitcherEntry.objects.values('espnid').distinct().filter(entry__uid__name=user.name)
	for es in pe:
		espnid = es['espnid']
		ps = PitcherEntry.objects.filter(entry__uid=user).filter(espnid=espnid)
		ip = 0
		name = ""
		for p in ps:
			ip = addIP(p.ip,ip)
			name = p.name
		#t1 = time.time()
		psagg = ps.aggregate(Sum('hits'),Sum('bbs'),Sum('ers'),Sum('ks'),Sum('w'),Sum('pts'))
		#t2 = time.time()
		#print t2-t1
		hits = psagg['hits__sum']
		ers = psagg['ers__sum']
		bbs = psagg['bbs__sum']
		ks = psagg['ks__sum']
		w = psagg['w__sum']
		pts = psagg['pts__sum']
		pi = [name,ip,hits,ers,bbs,ks,w,pts]
		c['P'].append(pi)
	#print c	
	for i in range(0,9):
		c['totals'][positions[i]] = []
		
		pe = PlayerEntry.objects.filter(entry__uid=user).filter(pos=positions[i])
		#print str(t2-t1) + "    totals"
		peagg = pe.aggregate(Sum('abs'),Sum('tbs'),Sum('runs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('pts'),Avg('salary'))
		
		ABs = peagg['abs__sum']
		RUNs = peagg['runs__sum']
		TBs = peagg['tbs__sum']
		RBIs = peagg['rbis__sum']
		BBs = peagg['bbs__sum']
		SBs = peagg['sbs__sum']
		PTs = peagg['pts__sum']
		salary = peagg['salary__avg']
		ptspersalary = round(float(PTs)/salary,3)
		p = [positionstr[i],positions[i],"",ABs,RUNs,TBs,RBIs,BBs,SBs,PTs,salary,ptspersalary ]
		c['totals'][positions[i]].append(p)
	#print c['totals']
	c['ptotals'] = TotalStats.objects.get(uid=user)
	for posi in range (0,9):
		c[positions[posi]] = sorted(c[positions[posi]], key=lambda p: p[3], reverse=True)
	message = render_to_response('statspos.html', c,context_instance=RequestContext(request))
	t2= time.time()
	#print t2-t1
	return HttpResponse(message)
	
	#for ent in user.entry_set.all():

def viewPlayerStats(request):
	params = {}
	if request.method=='GET':
		params = request.GET
	elif request.method=='POST':
		params = request.POST
	uid=params["uid"]
	
	getData(uid)
	
	print uid
	c = {}
	c['users'] = User.objects.all()	
	
	message = render_to_response('index.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

def viewTotalStatsHandler(request):
	args = dict()
	c = {}
	c['stats'] = TotalStats.objects.all()	
	message = render_to_response('totalstats.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

	

#http://games.espn.go.com/baseball-challenge/en/groupfind?objectStart=0&_=1311614072844&xhr=1


def getGroupUsers(id):
	url = "http://games.espn.go.com/baseball-challenge/en/group?sort=-1&groupID=" + id + "&view=default&periodStart=15&periodEnd=21&objectStart=" + str(start) + "&_=1311623122175&xhr=1"
	print url
#	print = "http://games.espn.go.com/baseball-challenge/en/group?groupID=80&entryID=90973&sort=-1&view=default&periodStart=15&objectStart=100&_=1311623493268&xhr=1"
	#baseball-challenge/en/groupfind?objectStart=60&_=1311619493877&xhr=1
	data = {}
	headers = {
	'Accept': 'text/html, */*',
	'Accept-Language': 'en-us,en;q=0.5',
	'Content-Type': 'application/x-www-form-urlencoded',
	'X-Requested-With': 'XMLHttpRequest',
	
	}
	req = urllib2.Request(url, data, headers)
	f = urllib2.urlopen(req)
	htmlSource = f.read()
	f.close()
	
	
	root = html.fromstring(htmlSource)
	leader = {}	
	leaders = root.cssselect("tr")
	x=1
	for i in leaders:
		line = tostring(i)
		if "oddrow" in line or "evenrow" in line:
			#print line.split('entryID=')[1].split('\"')[0]
			leader[x] = line.split('entryID=')[1].split('\"')[0]
			#print leader[x]
			getData(leader[x])
			x+=1
	return leader


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



def viewTransactionLog(request):
	params = {}
	if request.method=='GET':
		params = request.GET
	elif request.method=='POST':
		params = request.POST
	id=params["id"]
	
	user = User.objects.get(espnid=id)
	ent = Entry.objects.filter(uid=user)
	maxlog = UserTransactionLog.objects.filter(uid = user).aggregate(Max('gamenumber'))['gamenumber__max']
	maxent = Entry.objects.filter(uid = user).aggregate(Max('gamenumber'))['gamenumber__max']
	if not (maxlog==maxent):
		for e in ent:
			if e.gamenumber>1:
				prev = Entry.objects.get(uid=user,gamenumber = e.gamenumber-1)
				prevplayers = prev.players.all()
				prevpitcher = prev.pitchers.all()
				for p in e.players.all():
					position = p.pos
					#print p.name
					prevpos = prevplayers.get(pos=position)
					#print prevpos.name
					if not (prevpos.espnid == p.espnid):
						log = UserTransactionLog.objects.get_or_create(uid=user,dropped=prevpos.name,droppedat=prevpos.salary,added=p.name,addedat=p.salary,gamenumber=e.gamenumber)
						#log.save()
				for p in e.pitchers.all():
					prevpit = prevpitcher.get(entry__uid=user)###drop the filter?
					#print prevpit
				
					if not (prevpit.teamid == p.teamid):
						log = UserTransactionLog.objects.get_or_create(uid=user,dropped=prevpit.teamname,droppedat=prevpit.salary,added=p.teamname,addedat=p.salary,gamenumber=e.gamenumber)
						#log.save()
			else:
				if e.gamenumber == 1:
					for p in e.players.all():
						log = UserTransactionLog.objects.get_or_create(uid=user,dropped="Nobody",droppedat=0.0,added=p.name,addedat=p.salary,gamenumber=e.gamenumber)
						#log.save()
					for pi in e.pitchers.all():
						log = UserTransactionLog.objects.get_or_create(uid=user,dropped="Nobody",droppedat=0.0,added=p.teamname,addedat=p.salary,gamenumber=e.gamenumber)
						#log.save()
	c={}
	log = UserTransactionLog.objects.filter(uid=user)
	c['log'] = log
	c['total'] = log.count()
#	for i in UserTransactionLog.objects.all():
#		print i.added + " " + i.dropped
	message = render_to_response('viewlog.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

def getData(id):
	try:
		user = User.objects.get(espnid=id)
		if user.maxgame == None:
			max = 1
		else:
			max = user.maxgame
		if user.totalpoints == None:
			utpts = 0
		else:
			utpts = user.totalpoints
	except ObjectDoesNotExist:
		#ud = UserData(id)
		name = getUserName(id).decode('latin1')
		user = User(name=name, espnid=id)
		user.save()
		max = 1
		utpts = 0
	end = 124
	#print end
	for day in range(max,end):
		try:
		    ent = Entry.objects.get(uid=user,gamenumber=day)
		except ObjectDoesNotExist:
			player = parser(id,day)
			if player == 0:
				return 
			tpts = 0
			if player != None:
				ent = Entry.objects.create(uid=user,gamenumber=day,points=0)
				abs = 0;tbs = 0;runs = 0;rbis = 0;bbs = 0;sbs = 0
				ips = 0;phits = 0;pbbs = 0;ers = 0;ks = 0;ws = 0
				for i in player:
					if 'TB' in i:
						try:
							pl = PlayerEntry.objects.get(espnid =i['espnid'],gamenumber=int(day))
							tpts += pl.pts
						except ObjectDoesNotExist:
							pts = int(i['R']) + int(i['TB']) + int(i['RBI']) + int(i['BB']) + int(i['SB'])
							abs += int(i['AB'])
							tbs += int(i['TB'])
							runs += int(i['R'])
							rbis += int(i['RBI'])
							bbs += int(i['BB'])
							sbs += int(i['SB'])
							tpts += pts
							pl = PlayerEntry(espnid=i['espnid'],gamenumber=int(day),pos=i['pos'],bbcid=i['id'],doubleheader=i['dh'],nogame=i['nogame'],abs=i['AB'],runs=i['R'],tbs=i['TB'],rbis=i['RBI'],bbs=i['BB'],sbs=i['SB'],pts=pts,salary=i['salary'],teamid=i['teamid'],teamname=teams.team[int(i['teamid'])],name = i['FN'] + " " + i['LN'])
							#print "not created"
							pl.save()						
						ent.players.add(pl)
					if 'IP' in i:
						try:
							pi = PitcherEntry.objects.get(teamid=i['teamid'],gamenumber=int(day))
							tpts += pi.pts
						except ObjectDoesNotExist:
							ipfrac = int(round((float(i['IP'])-round(float(i['IP'])))*10,0))
							ip = round(float(i['IP']))*3+ipfrac
							ips += addIP(ip,ips)
							phits += int(i['H'])
							pbbs += int(i['BB'])
							ers += int(i['ER'])
							ks += int(i['K'])
							ws += int(i['W'])
							
							name = teams.team[int(i['teamid'])]
							pts = ip + int(i['K']) - int(i['H']) - (3*int(i['ER'])) - int(i['BB']) + (5*(int(i['W'])))
							tpts += pts
						#print i
							pi = PitcherEntry(name = name, ip = i['IP'], gamenumber=int(day), espnid = i['id'], espnid2 = i['id2'], doubleheader = i['dh'], nogame = i['nogame'], hits = i['H'], ers = i['ER'], bbs = i['BB'], ks = i['K'], w = i['W'], pts = pts, salary =i['salary'], teamid =i['teamid'], teamname=teams.team[int(i['teamid'])])
							pi.save()
						ent.pitchers.add(pi)				
				ent.abs = abs
				ent.tbs = tbs
				ent.runs = runs
				
				ent.rbis = rbis
				ent.bbs = bbs
				ent.sbs = sbs
				ent.ips = 0
				#pi = ent.pitchers.all()
				#aggp = pi.aggregate(Sum('hits'),Sum('bbs'),Sum('ers'),Sum('ks'),Sum('w'))
				
				ent.ips = ips
				ent.phits = phits
				ent.pbbs = pbbs
				ent.ers = ers
				ent.ks = ks
				ent.ws = ws
				if ent.ers > 0:
					ent.era = float(ent.ers*9)/(float(ipToOuts(ent.ips))/3)
				else:
					ent.era = 0
				if ent.abs > 0:
					ent.slug = float(ent.tbs) /float(ent.abs)
					ent.ptsabs = float(ent.tbs+ent.runs+ent.rbis+ent.bbs+ent.sbs)/float(ent.abs)
				else:
					ent.slug = 0
					ent.ptsabs = 0
				if ent.runs > ent.ers:
					ent.runwin = 1
				else:
					if ent.runs == ent.ers:
						ent.runtie = 1
					else:
						ent.runloss = 1
				if ent.rbis > ent.ers:
					ent.rbiwin = 1
				else:
					if ent.rbis == ent.ers:
						ent.rbitie = 1
					else:
						ent.rbiloss = 1
	
				utpts += tpts
				ent.points = tpts
				ent.save()
	for i in range(1,30):
		totalStatsTeamUpdater(user,i,end)
	#print "stats done"
	#print user.name
	totalStatsUpdater(user,end)
	user.maxgame = end
	user.totalpoints = utpts
	user.save()
	#pl = PlayerEntry.objects.all()
	#print pl.count()
	#pi = PitcherEntry.objects.all()
	#print pi.count()


def getDataNew(id):
	file = "/Users/Jason/bbcdata/entrysql" + ".db"
	conn = sqlite3.connect(file)
	c = conn.cursor()
	try:
		user = User.objects.get(espnid=id)
		if user.maxgame == None:
			max = 1
		else:
			max = user.maxgame
		if user.totalpoints == None:
			utpts = 0
		else:
			utpts = user.totalpoints
	except ObjectDoesNotExist:
		#ud = UserData(id)
		name = getUserName(id).decode('latin1')
		user = User(name=name, espnid=id)
		user.save()
		max = 1
		utpts = 0
	end = 124
	#print end
	for day in range(1,end):
		try:
		    ent = Entry.objects.get(uid=user,gamenumber=day)
		except ObjectDoesNotExist:
			#change for null
			ent = Entry.objects.create(uid=user,gamenumber=day,points=0)
			tpts = 0
			abs = 0;tbs = 0;runs = 0;rbis = 0;bbs = 0;sbs = 0
			ips = 0;phits = 0;pbbs = 0;ers = 0;ks = 0;ws = 0
			
			#player = parser(id,day)
			key = id *100000 + day
			c.execute("SELECT * FROM catcher WHERE id = ?", (key,))
			catcher = c.fetchone()
			c.execute("SELECT * FROM firstbase WHERE id = ?", (key,))
			firstbase = c.fetchone()
			c.execute("SELECT * FROM secondbase WHERE id = ?", (key,))
			secondbase = c.fetchone()
			c.execute("SELECT * FROM thirdbase WHERE id = ?", (key,))
			thirdbase = c.fetchone()
			c.execute("SELECT * FROM shortstop WHERE id = ?", (key,))
			shortstop = c.fetchone()
			c.execute("SELECT * FROM leftfield WHERE id = ?", (key,))
			leftfield = c.fetchone()
			c.execute("SELECT * FROM centerfield WHERE id = ?", (key,))
			centerfield = c.fetchone()
			c.execute("SELECT * FROM rightfield WHERE id = ?", (key,))
			rightfield = c.fetchone()
			c.execute("SELECT * FROM dh WHERE id = ?", (key,))
			dh = c.fetchone()
			c.execute("SELECT * FROM ps WHERE id = ?", (key,))
			ps = c.fetchone()
			try:
				pl = PlayerEntry.objects.get(espnid =catcher[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(catcher[11]) + int(catcher[12]) + int(catcher[13]) + int(catcher[14]) + int(catcher[15])
				abs += int(catcher[10])
				tbs += int(catcher[15])
				runs += int(catcher[12])
				rbis += int(catcher[13])
				bbs += int(catcher[11])
				sbs += int(catcher[14])
				tpts += pts
				pl = PlayerEntry(espnid=catcher[5],gamenumber=int(day),pos="C",bbcid=catcher[6],doubleheader=catcher[16],nogame=catcher[18],abs=catcher[10],runs=catcher[12],tbs=catcher[15],rbis=catcher[13],bbs=catcher[11],sbs=catcher[14],pts=pts,salary=catcher[8],teamid=catcher[7],teamname=teams.team[int(catcher[7])],name = catcher[3] + " " + catcher[4])
				
				pl.save()
			ent.players.add(pl)
			try:
				pl = PlayerEntry.objects.get(espnid =firstbase[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(firstbase[11]) + int(firstbase[12]) + int(firstbase[13]) + int(firstbase[14]) + int(firstbase[15])
				abs += int(firstbase[10])
				tbs += int(firstbase[15])
				runs += int(firstbase[12])
				rbis += int(firstbase[13])
				bbs += int(firstbase[11])
				sbs += int(firstbase[14])
				tpts += pts
				pl = PlayerEntry(espnid=firstbase[5],gamenumber=int(day),pos="C",bbcid=firstbase[6],doubleheader=firstbase[16],nogame=firstbase[18],abs=firstbase[10],runs=firstbase[12],tbs=firstbase[15],rbis=firstbase[13],bbs=firstbase[11],sbs=firstbase[14],pts=pts,salary=firstbase[8],teamid=firstbase[7],teamname=teams.team[int(firstbase[7])],name = firstbase[3] + " " + firstbase[4])

				pl.save()
			ent.players.add(pl)	
			try:
				pl = PlayerEntry.objects.get(espnid =secondbase[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(secondbase[11]) + int(secondbase[12]) + int(secondbase[13]) + int(secondbase[14]) + int(secondbase[15])
				abs += int(secondbase[10])
				tbs += int(secondbase[15])
				runs += int(secondbase[12])
				rbis += int(secondbase[13])
				bbs += int(secondbase[11])
				sbs += int(secondbase[14])
				tpts += pts
				pl = PlayerEntry(espnid=secondbase[5],gamenumber=int(day),pos="C",bbcid=secondbase[6],doubleheader=secondbase[16],nogame=secondbase[18],abs=secondbase[10],runs=secondbase[12],tbs=secondbase[15],rbis=secondbase[13],bbs=secondbase[11],sbs=secondbase[14],pts=pts,salary=secondbase[8],teamid=secondbase[7],teamname=teams.team[int(secondbase[7])],name = secondbase[3] + " " + secondbase[4])

				pl.save()
			ent.players.add(pl)	
			try:
				pl = PlayerEntry.objects.get(espnid =thirdbase[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(thirdbase[11]) + int(thirdbase[12]) + int(thirdbase[13]) + int(thirdbase[14]) + int(thirdbase[15])
				abs += int(thirdbase[10])
				tbs += int(thirdbase[15])
				runs += int(thirdbase[12])
				rbis += int(thirdbase[13])
				bbs += int(thirdbase[11])
				sbs += int(thirdbase[14])
				tpts += pts
				pl = PlayerEntry(espnid=thirdbase[5],gamenumber=int(day),pos="C",bbcid=thirdbase[6],doubleheader=thirdbase[16],nogame=thirdbase[18],abs=thirdbase[10],runs=thirdbase[12],tbs=thirdbase[15],rbis=thirdbase[13],bbs=thirdbase[11],sbs=thirdbase[14],pts=pts,salary=thirdbase[8],teamid=thirdbase[7],teamname=teams.team[int(thirdbase[7])],name = thirdbase[3] + " " + thirdbase[4])

				pl.save()
			ent.players.add(pl)
			try:
				pl = PlayerEntry.objects.get(espnid =shortstop[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(shortstop[11]) + int(shortstop[12]) + int(shortstop[13]) + int(shortstop[14]) + int(shortstop[15])
				abs += int(shortstop[10])
				tbs += int(shortstop[15])
				runs += int(shortstop[12])
				rbis += int(shortstop[13])
				bbs += int(shortstop[11])
				sbs += int(shortstop[14])
				tpts += pts
				pl = PlayerEntry(espnid=shortstop[5],gamenumber=int(day),pos="C",bbcid=shortstop[6],doubleheader=shortstop[16],nogame=shortstop[18],abs=shortstop[10],runs=shortstop[12],tbs=shortstop[15],rbis=shortstop[13],bbs=shortstop[11],sbs=shortstop[14],pts=pts,salary=shortstop[8],teamid=shortstop[7],teamname=teams.team[int(shortstop[7])],name = shortstop[3] + " " + shortstop[4])

				pl.save()
			ent.players.add(pl)	
			try:
				pl = PlayerEntry.objects.get(espnid =leftfield[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(leftfield[11]) + int(leftfield[12]) + int(leftfield[13]) + int(leftfield[14]) + int(leftfield[15])
				abs += int(leftfield[10])
				tbs += int(leftfield[15])
				runs += int(leftfield[12])
				rbis += int(leftfield[13])
				bbs += int(leftfield[11])
				sbs += int(leftfield[14])
				tpts += pts
				pl = PlayerEntry(espnid=leftfield[5],gamenumber=int(day),pos="C",bbcid=leftfield[6],doubleheader=leftfield[16],nogame=leftfield[18],abs=leftfield[10],runs=leftfield[12],tbs=leftfield[15],rbis=leftfield[13],bbs=leftfield[11],sbs=leftfield[14],pts=pts,salary=leftfield[8],teamid=leftfield[7],teamname=teams.team[int(leftfield[7])],name = leftfield[3] + " " + leftfield[4])

				pl.save()
			ent.players.add(pl)
			try:
				pl = PlayerEntry.objects.get(espnid =centerfield[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(centerfield[11]) + int(centerfield[12]) + int(centerfield[13]) + int(centerfield[14]) + int(centerfield[15])
				abs += int(centerfield[10])
				tbs += int(centerfield[15])
				runs += int(centerfield[12])
				rbis += int(centerfield[13])
				bbs += int(centerfield[11])
				sbs += int(centerfield[14])
				tpts += pts
				pl = PlayerEntry(espnid=centerfield[5],gamenumber=int(day),pos="C",bbcid=centerfield[6],doubleheader=centerfield[16],nogame=centerfield[18],abs=centerfield[10],runs=centerfield[12],tbs=centerfield[15],rbis=centerfield[13],bbs=centerfield[11],sbs=centerfield[14],pts=pts,salary=centerfield[8],teamid=centerfield[7],teamname=teams.team[int(centerfield[7])],name = centerfield[3] + " " + centerfield[4])

				pl.save()
			ent.players.add(pl)	
			try:
				pl = PlayerEntry.objects.get(espnid =rightfield[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(rightfield[11]) + int(rightfield[12]) + int(rightfield[13]) + int(rightfield[14]) + int(rightfield[15])
				abs += int(rightfield[10])
				tbs += int(rightfield[15])
				runs += int(rightfield[12])
				rbis += int(rightfield[13])
				bbs += int(rightfield[11])
				sbs += int(rightfield[14])
				tpts += pts
				pl = PlayerEntry(espnid=rightfield[5],gamenumber=int(day),pos="C",bbcid=rightfield[6],doubleheader=rightfield[16],nogame=rightfield[18],abs=rightfield[10],runs=rightfield[12],tbs=rightfield[15],rbis=rightfield[13],bbs=rightfield[11],sbs=rightfield[14],pts=pts,salary=rightfield[8],teamid=rightfield[7],teamname=teams.team[int(rightfield[7])],name = rightfield[3] + " " + rightfield[4])

				pl.save()
			ent.players.add(pl)
			try:
				pl = PlayerEntry.objects.get(espnid =dh[5],gamenumber=int(day))
				tpts += pl.pts
			except ObjectDoesNotExist:
				pts = int(dh[11]) + int(dh[12]) + int(dh[13]) + int(dh[14]) + int(dh[15])
				abs += int(dh[10])
				tbs += int(dh[15])
				runs += int(dh[12])
				rbis += int(dh[13])
				bbs += int(dh[11])
				sbs += int(dh[14])
				tpts += pts
				pl = PlayerEntry(espnid=dh[5],gamenumber=int(day),pos="C",bbcid=dh[6],doubleheader=dh[16],nogame=dh[18],abs=dh[10],runs=dh[12],tbs=dh[15],rbis=dh[13],bbs=dh[11],sbs=dh[14],pts=pts,salary=dh[8],teamid=dh[7],teamname=teams.team[int(dh[7])],name = dh[3] + " " + dh[4])

				pl.save()
			
			ent.players.add(pl)
			
			
			try:
				pi = PitcherEntry.objects.get(teamid=ps[11],gamenumber=int(day))
				tpts += pi.pts
			except ObjectDoesNotExist:
				ipfrac = int(round((float(ps[14])-round(float(ps[14])))*10,0))
				ip = round(float(ps[14]))*3+ipfrac
				ips += addIP(ip,ips)
				phits += int(ps[15])
				pbbs += int(ps[17])
				ers += int(ps[16])
				ks += int(ps[18])
				ws += int(ps[19])
				
				name = teams.team[int(ps[11])]
				pts = ip + int(ps[18]) - int(ps[15]) - (3*int(ps[16])) - int(ps[17]) + (5*(int(ps[19])))
				tpts += pts
			#print i
				pi = PitcherEntry(name = name, ip = ps[14], gamenumber=int(day), espnid = ps[9], espnid2 = ps[10], doubleheader = ps[20], nogame = ps[22], hits = ps[15], ers = ps[16], bbs = ps[17], ks = ps[18], w = ps[19], pts = pts, salary = ps[12], teamid = ps[11], teamname=teams.team[int(ps[11])])
				pi.save()
			ent.pitchers.add(pi)
			
			
			
			ent.abs = abs
			ent.tbs = tbs
			ent.runs = runs
			
			ent.rbis = rbis
			ent.bbs = bbs
			ent.sbs = sbs
			ent.ips = 0
			#pi = ent.pitchers.all()
			#aggp = pi.aggregate(Sum('hits'),Sum('bbs'),Sum('ers'),Sum('ks'),Sum('w'))
			
			ent.ips = ips
			ent.phits = phits
			ent.pbbs = pbbs
			ent.ers = ers
			ent.ks = ks
			ent.ws = ws
			if ent.ers > 0:
				ent.era = float(ent.ers*9)/(float(ipToOuts(ent.ips))/3)
			else:
				ent.era = 0
			if ent.abs > 0:
				ent.slug = float(ent.tbs) /float(ent.abs)
				ent.ptsabs = float(ent.tbs+ent.runs+ent.rbis+ent.bbs+ent.sbs)/float(ent.abs)
			else:
				ent.slug = 0
				ent.ptsabs = 0
			if ent.runs > ent.ers:
				ent.runwin = 1
			else:
				if ent.runs == ent.ers:
					ent.runtie = 1
				else:
					ent.runloss = 1
			if ent.rbis > ent.ers:
				ent.rbiwin = 1
			else:
				if ent.rbis == ent.ers:
					ent.rbitie = 1
				else:
					ent.rbiloss = 1

			utpts += tpts
			ent.points = tpts
			ent.save()
			
	for i in range(1,30):
		totalStatsTeamUpdater(user,i,end)
	#print "stats done"
	#print user.name
	totalStatsUpdater(user,end)
	user.maxgame = end
	user.totalpoints = utpts
	user.save()
	#pl = PlayerEntry.objects.all()
	#print pl.count()
	#pi = PitcherEntry.objects.all()
	#print pi.count()




def UserData(id):
	s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
	
	file = "/Users/Jason/bbcdata/userdata/" + str(date.today().month) + "." + str(date.today().day) + "." + str(id) + ".html.gz"
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
		headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		}
		request = urllib2.Request(s,{},headers)
		response = urllib2.urlopen(request)
		if response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO( response.read())
			f = gzip.GzipFile(fileobj=buf)
			data = f.read()
			output = gzip.open(file, 'wb')
			output.write(data)
			output.close()
	infile = open(file,"r")
	gzipper = gzip.GzipFile(fileobj=infile)
	htmlsource = gzipper.read()
	
	#soup = BeautifulSoup(htmlsource)
	#title = soup.title
	#root = html.fromstring(htmlsource)
	ss = htmlsource.split("<h1 style=\"display:inline;\">")[1].split("</h1>")[0]
	#ss = ss.replace('\xb4','')
	#title = root.cssselect("title")
	
	#ss = tostring(title[0])
	#ss = ss.split('<title>ESPN - Baseball Challenge - |')[0]
	
	#ss = re.split('<title>ESPN - Baseball Challenge - |</title>', tostring(title[0]))
	
	#ss = filter(None, ss)
	
#	x = soup.find("div", { "class" : "games-graph-data" })
	
#	em= str(x)
	
#	li = re.split('<em>|</em>',em)
	
#	for i in li:
#		for n in i:
#			if n.isdigit():
#				break;
#			else:
#				li.remove(i)
#				break;
	
	userdata = {}
	userdata['name'] = ss
#	userdata['rank'] = li[2]
#	userdata['pct'] = li[1]
	return userdata

def viewTop100Lineup(request):
	c = {}
	try:
		top = Top100Lineup.objects.get(date=date.today())
	except ObjectDoesNotExist:
		top = Top100Lineup.objects.create(date=date.today())
		leaders = getLeaders()
		for i in range(1,len(leaders)+1):
			l = parserLineup(leaders[i])
			line = Lineup.objects.create(name=UserData(leaders[i])['name'])
			for i in l:
				if i['pos']=="C":
					line.catcher = i['espnid']
					line.catchername = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="1B":
					line.firstbase = i['espnid']
					line.firstbasename = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="2B":
					line.secondbase = i['espnid']
					line.secondbasename = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="3B":
					line.thirdbase = i['espnid']
					line.thirdbasename = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="SS":
					line.shortstop = i['espnid']
					line.shortstopname = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="LF":
					line.leftfield = i['espnid']
					line.leftfieldname = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="CF":
					line.centerfield = i['espnid']
					line.centerfieldname = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="RF":
					line.rightfield = i['espnid']
					line.rightfieldname = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="DH":
					line.dh = i['espnid']
					line.dhname = i['FN'] + " " + i['LN']
					getHeadShot(i['espnid'])
				if i['pos']=="PS":
					line.ps = i['id']
					if 'p1FN' in i:
						line.psname = i['p1FN'] + " " + i['p1LN']
					getHeadShot(i['id'])
				line.save()
			top.top100.add(line)
			top.save()
	c['lineup'] = Top100Lineup.objects.get(date=date.today()).top100.all()
	
	message = render_to_response('top100.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)

		
	
def getLeaders(request):
	file = "/Users/Jason/bbcdata/leaderboard/" + "dayscoring" + "." + str(date.today().month) + "." + str(date.today().day) + ".html.gz"
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/leaderboard?segment=-1&scoringSystemID=2&periodStart=15&univ=0"
		headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		}
		request = urllib2.Request(s,{},headers)
		response = urllib2.urlopen(request)
		if response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO( response.read())
			f = gzip.GzipFile(fileobj=buf)
			data = f.read()
			output = gzip.open(file, 'wb')
			output.write(data)
			output.close()
	infile = open(file,"r")
	gzipper = gzip.GzipFile(fileobj=infile)
	htmlsource = gzipper.read()
	root = html.fromstring(htmlsource)
	leader = {}	
	leaders = root.cssselect("tr")
	x=1
	for i in leaders:
		line = tostring(i)
		if "oddrow" in line or "evenrow" in line:
			#print line.split('entryID=')[1].split('\"')[0]
			leader[x] = line.split('entryID=')[1].split('\"')[0]
			getData(leader[x])
			#print leader[x]
			x+=1
	return leader

def parserLineup(id):
	file = "/Users/Jason/bbcdata/lineup/" + str(date.today()) + " " + str(id) + ".html.gz"
	
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id)
		headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		}
		request = urllib2.Request(s,{},headers)
		response = urllib2.urlopen(request)
		if response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO( response.read())
			f = gzip.GzipFile(fileobj=buf)
			data = f.read()
			output = gzip.open(file, 'wb')
			output.write(data)
			output.close()
		if response.read() == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">":
			return
	infile = open(file,"r")
	gzipper = gzip.GzipFile(fileobj=infile)
	htmlsource = gzipper.read()
	if htmlsource == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">":
		#print "no data"
		return
	root = html.fromstring(htmlsource)
	data = root.cssselect('tbody')
	
	pl = data[0].cssselect('tr')	
	
	player = [{},{},{},{},{},{},{},{},{},{}]
	i = 0
	
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
			player[i]['nogame'] = False
			player[i]['oppteamid'] = tostring(l1[3]).split('teamId=')[1].split('\"')[0]
			if l1[5].text == None:
				player[i]['dh'] = True
		else:
			player[i]['nogame'] = True
		if "@" in str(l1[3]):
			player[i]['loc'] = "Away"
		else:
			player[i]['loc'] = "Home"
		l=0
		i+=1
	p = data[1].cssselect("td")
	player[9]['pos'] = "PS"
	p2 = tostring(p[2])
	player[9]['id'] = 0
	player[9]['id2'] = 0
	player[9]['teamid'] = p2.split('tid=\"')[1].split('\"')[0]
	player[9]['dh'] = False
	if p[3].text != "--":
		player[9]['nogame'] = False
		if "\"roster-plyr\"" in p2:
			player[9]['id'] = p2.split('playerId=')[1].split('\"')[0]
			arr = getNameFromESPNID(player[9]['id'])
			player[9]['p1FN'] = arr['FN']
			player[9]['p1LN'] = arr['LN']
			player[9]['p1SUF'] = arr['suffix']
		player[9]['oppteamid'] = tostring(p[3]).split('teamId=')[1].split('\"')[0]
		if p[5].text == None:
			player[9]['id2'] = p2.split('playerId=')[2].split('\"')[0]
			arr = getNameFromESPNID(player[9]['id2'])
			player[9]['p2FN'] = arr['FN']
			player[9]['p2LN'] = arr['LN']
			player[9]['p2SUF'] = arr['suffix']
			player[9]['dh'] = True
	else:
		player[9]['nogame'] = True
	player[9]['salary'] = tostring(p[12]).strip('<>td  = clasnobr///"')
	return player


def getNameFromESPNID(id):
	file = "/Users/Jason/bbcdata/player/" + str(id)
	if not (os.path.isfile(file)):
		s = "http://m.espn.go.com/mlb/playercard?playerId=" + str(id) + "&wjb"
		
		request = urllib2.Request(s)
		request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
		
		sock = urllib2.urlopen(s)
		opener = urllib2.build_opener()
		source = open(file,"wb")
		source.writelines(opener.open(request).read())
		source.close()
	infile = open(file,"r")
	htmlsource = infile.read()
	title = htmlsource.split("<div class=\"sub bold\">")[1].split("<")[0].split(" ")
	i={}
	i['num'] = title[0]
	i['FN'] = title[1]
	i['LN'] = title[2]
	if len(title)>3:
		i['suffix'] = title[3]
	else:
		i['suffix'] = None
	return i	


def getAllUsers():
	file = "/Users/Jason/entries small.txt"
	infile = open(file,"r")
	i = infile.readlines()
	for x in i:
		if x != "entries.txt":
			t1 = time.time()
			id = int(x.split("\n")[0])
			print id
			getData(id)
			t2 = time.time()
			print t2-t1
	#c={}
	#return HttpResponse('index.html', c,context_instance=RequestContext(request))


def parser(id,day):
	t1 = time.time()
		#print day
	file = "/Users/Jason/bbcdata/entry/" + str(id) + "/" + "spid=" + str(day) + ".html.gz"
	#print file
	#path = "/Users/Jason/bbcdata/entry/" + str(id) + "/"
	#if not os.path.exists(path): os.makedirs(path)
	if not (os.path.isfile(file)):
		h = httplib2.Http()
		#print "need to dl " + str(file)
		s = "http://games.espn.go.com/baseball-challenge/en/format/ajax/getBoxscoreSnapshot?entryID=" + str(id) + "&spid=" + str(day)
		headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		'Connection':	'Keep-Alive',
		}
		#request = urllib2.Request(s,{},headers)
		#response = urllib2.urlopen(request)
		
		response, content = h.request(s,headers=headers)
		#print content
		#if response.info().get('Content-Encoding') == 'gzip':
		
		output = gzip.open(file, 'wb')
		output.write(content)
		output.close()
	t3 = time.time()		
	infile = open(file,"r")
	gzipper = gzip.GzipFile(fileobj=infile)
	htmlsource = gzipper.read()

	if htmlsource == "No set roster for entry<input type=hidden id=\"setInterval\" value=\"0\">" or htmlsource == '':
		#print "no data"
		return
		
	root = html.fromstring(htmlsource)
	data = root.cssselect('tbody')
	pl = data[0].cssselect('tr')	
	t4 = time.time()
	#print t4 - t3
	player = [{},{},{},{},{},{},{},{},{},{}]
	stat={5:"AB",6:"R",7:"TB",8:"RBI",9:"BB",10:"SB"}
	i = 0
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
			player[i]['nogame'] = False
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
		else:
			player[i]['nogame'] = True
			for j in range(5,11):
				player[i][stat[j]] = 0
		if "@" in str(l1[3]):
			player[i]['loc'] = "Away"
		else:
			player[i]['loc'] = "Home"
		l=0
		i+=1
	p = data[1].cssselect("td")
	player[9]['pos'] = "PS"
	p2 = tostring(p[2])
	player[9]['id'] = 0
	player[9]['id2'] = 0
	player[9]['teamid'] = p2.split('tid=\"')[1].split('\"')[0]
	player[9]['dh'] = False
	statps={5:"IP",6:"H",7:"ER",8:"BB",9:"K",10:"W"}
	if p[3].text != "--":
		player[9]['nogame'] = False
		if "\"roster-plyr\"" in p2:
			player[9]['id'] = p2.split('playerId=')[1].split('\"')[0]
			arr = getNameFromESPNID(player[9]['id'])
			player[9]['p1FN'] = arr['FN']
			player[9]['p1LN'] = arr['LN']
			player[9]['p1SUF'] = arr['suffix']
		player[9]['oppteamid'] = tostring(p[3]).split('teamId=')[1].split('\"')[0]
		if p[5].text == None:
			player[9]['id2'] = p2.split('playerId=')[2].split('\"')[0]
			arr = getNameFromESPNID(player[9]['id2'])
			player[9]['p2FN'] = arr['FN']
			player[9]['p2LN'] = arr['LN']
			player[9]['p2SUF'] = arr['suffix']
			player[9]['dh'] = True
			for j in range(5,11):
				s1 = p[j].cssselect('span')[0]
				s2 = p[j].cssselect('span')[1]
				player[9][statps[j]] = addIP(s1.text,s2.text)			
		else:
			for j in range(5,11):
				player[9][statps[j]] = p[j].text
	else:
		player[9]['nogame'] = True
		for j in range(5,11):
			player[9][statps[j]] = 0
	player[9]['salary'] = tostring(p[12]).strip('<>td  = clasnobr///"')
	t2 = time.time()
	print str(t2 - t1) + " day " + str(day) 
	return player


def getUserName(id):
	s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
	file = "/Users/Jason/bbcdata/usernames/" + str(id) + ".txt"
	path = "/Users/Jason/bbcdata/usernames/"
	#if not os.path.exists(path): os.makedirs(path)
	if not (os.path.isfile(file)):
		s = "http://games.espn.go.com/baseball-challenge/en/entry?entryID=" + str(id)
		headers = {
		'Accept': 'text/html, */*',
		'Accept-Language': 'en-us,en;q=0.5',
		'Accept-Encoding':	'gzip, deflate',
		'Connection':	'Keep-Alive',
		}
		response, content = h.request(s,headers=headers)
		source = open(file,"w")
		
		ss = content.split("<h1 style=\"display:inline;\">")[1].split("</h1>")[0]
		print "id = " + str(id) + " " + str(ss)
		source.write(ss)
		source.close()
	infile = open(file,"r")
	return infile.read()


def getHeadShot(id):
	#t = []
	file = "/Users/Jason/bbcdata/headshots/" + str(id) + ".jpg"
	if not (os.path.isfile(file)):
		s = "http://a.espncdn.com/i/headshots/mlb/players/65/" + str(id) + ".jpg"
		
		request = urllib2.Request(s)
		request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
		
		#sock = urllib2.urlopen(s)
		opener = urllib2.build_opener()
		source = open(file,"wb")
		try:
		    resp = opener.open(request)
		except urllib2.URLError, e:
			request2 = urllib2.Request("http://a.espncdn.com/i/columnists/nophoto_65x90.gif")
			request2.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1')
			opener2 = urllib2.build_opener()
			resp2 = opener2.open(request2)
			source.writelines(resp2.read())
			source.close()
		else:
			source.writelines(resp.read())
			source.close()
