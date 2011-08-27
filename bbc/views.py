
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
from endless_pagination.decorators import page_template, page_templates

from datetime import datetime
from bbcstats.bbc.models import *
from datetime import date
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
	ipf = ipf1+ipf2
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
		tot = TotalStats(uid=user)
	
	entry = Entry.objects.filter(uid=user)
	
	agg = entry.all().aggregate(Sum('abs'),Sum('tbs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('runs'),Sum('phits'),Sum('pbbs'),Sum('ers'),Sum('ks'),Sum('ws'),Sum('rbiwin'),Sum('rbitie'),Sum('rbiloss'),Sum('runwin'),Sum('runtie'),Sum('runloss'),Sum('points'))
	tot.abs = agg['abs__sum']
	tot.tbs = agg['tbs__sum']
	tot.rbis = agg['rbis__sum']
	tot.bbs = agg['bbs__sum']
	tot.sbs = agg['sbs__sum']
	tot.runs = agg['runs__sum']
	ips=0
	for p in entry.all():
		#print p.ips
		ips = addIP(ips,p.ips)
	tot.ips = ips
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
		tot = TotalTeamStats(uid=user,teamid=teamid)
		
	pla = PlayerEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
	if pla.count>0:
		agg = pla.all().aggregate(Sum('abs'),Sum('tbs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('runs'))
		tot.abs = agg['abs__sum']
		tot.tbs = agg['tbs__sum']
		tot.rbis = agg['rbis__sum']
		tot.bbs = agg['bbs__sum']
		tot.sbs = agg['sbs__sum']
		tot.runs = agg['runs__sum']
		if tot.abs > 0:
			tot.slug = float(tot.tbs) /float(tot.abs)
			tot.ptsabs = float(tot.tbs+tot.runs+tot.rbis+tot.bbs+tot.sbs)/float(tot.abs)
		else:
			tot.slug = 0
			tot.ptsabs = 0
	
	pit = PitcherEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
	if pit.count()>0:
		for p in pit.all():
			tot.ips = addIP(tot.ips,p.ip)
		aggp = pit.all().aggregate(Sum('hits'),Sum('bbs'),Sum('ers'),Sum('ks'),Sum('w'))
		tot.phits = aggp['hits__sum']
		tot.pbbs = aggp['bbs__sum']
		tot.ers = aggp['ers__sum']
		tot.ks = aggp['ks__sum']
		tot.ws = aggp['w__sum']
		if tot.ers > 0:
			tot.era = float(tot.ers*9)/(float(ipToOuts(tot.ips))/3)
		else:
			tot.era = 0
	
	
	###FIX
	tot.points = 0
	tot.maxgame= maxgame
	tot.save()
	#print tot


@page_template("index_page.html", key="index_page")
def HomeHandler(request,template="index.html",extra_context=None):	
	#params= request.GET
	
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
	
	#paginator = Paginator(q, 10)
	#try:
	#	page = int(request.GET.get('page', '1'))
	#except ValueError:
	#	page = 1
    # If page request (9999) is out of range, deliver last page of results.
	#try:
	#	qs = paginator.page(page)
	#except (EmptyPage, InvalidPage):
	#	qs = paginator.page(paginator.num_pages)
	#getAllUsers()
	
	#getData(18989)
	getDataNew(100019)
	#getAllUsers()
	context = {
	        'objects': q,
			'page_template': page_template,
	}
	pt = "index_page.html"
	if request.is_ajax():
		template = pt

#	if extra_context is not None:
#		context.update(extra_context)
	return render_to_response(template, context,
		context_instance=RequestContext(request))


	
	#if extra_context is not None:
	#	context.update(extra_context)
#	return render_to_response(template, context, context_instance=RequestContext(request))
	
	
	#message = render_to_response('index.html', c,context_instance=RequestContext(request))
	#return HttpResponse(message)

	
def StatsHandler(request):
	args = dict()
	c = {}
	
	u = User.objects.all()
#	for user in u:
	for i in range(1,0):
		t1 = time.time()
		max_game = Entry.objects.filter(uid=user).aggregate(Max('gamenumber'))['gamenumber__max']
		if (((max_game != max_game_stat)) or max_game_stat == None) and max_game != None:
			for i in range(1,max_game+1):	
				for i in range(1,30):
					totalStatsTeamUpdater(user,i,max_game)
			totalStatsUpdater(user,max_game)
			t2 = time.time()
			print t2-t1
	u = User.objects.all()
	
	print "stats done"
	c['stats'] = TotalStats.objects.all()
	
	message = render_to_response('stats.html', c,context_instance=RequestContext(request))
	return HttpResponse(message)


def PositionStatsHandler(request):
	params= request.GET
	id = params["id"]
	t1 = time.time()
	user = User.objects.get(espnid=id)
	maxgame = Entry.objects.filter(uid=user).aggregate(Max('gamenumber'))['gamenumber__max']
	done = False
	try:
		pos = PositionPlayerStats.objects.get(uid=user,pos=0)
		if pos.maxgame >= maxgame:
			done = True
	except ObjectDoesNotExist:
		done = False
	
	print done
	positions = ["C","1B","2B","3B","SS","LF","CF","RF","DH"]
	positionstr = ["Catcher", "First Base", "Second Base", "Third Base", "Shortstop", "Left Field", "Center Field", "Right Field", "Designated Hitter"]
	c={'pos':[], 'C':[],'1B':[],'2B':[],'3B':[],'SS':[],'LF':[],'CF':[],'RF':[],'DH':[],'totals':{},'sums':[],'P':[]}
	#c['sums'] = TotalStats.objects.get(uid=user)
	c['pos']=positions
	if not done:
		for i in range (0,9):
			pe = PlayerEntry.objects.filter(entry__uid=user)
			e = pe.values_list('espnid', flat=True).distinct().filter(pos=positions[i])
			for es in e:
				try:
					play = PlayerStat.objects.get(uid = user, espnid = es)
					maxgamep = play.maxgame
					exists = True
				except ObjectDoesNotExist:
					maxgamep = 0
					exists = False
				#not sure if needed

				if maxgamep <= maxgame:

					espnid = es
				
					peespn = pe.filter(espnid=espnid)
					#print peespn.count()
			
					#t3 = time.time()
					#peagg = peespn.aggregate(Sum('abs'))
					#t4 = time.time()
					#print str(t4-t3) + " values"
					#t1 = time.time()
					peagg = peespn.aggregate(Sum('abs'),Sum('tbs'),Sum('runs'),Sum('tbs'),Sum('runs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('pts'))
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
					#salary = peagg['salary__avg']
					#ptspersalary = round(float(PTs)/salary,3)
			
					pl = PlayerEntry.objects.filter(espnid=espnid)
			
					name = ""
					for pp in pl:
						name = pp.name
						espnid = pp.espnid
						bbcid = pp.bbcid
						teamid = pp.teamid
						break
					if exists:
						play.abs = ABs
						play.tbs = TBs
						play.rbis = RBIs
						play.bbs = BBs
						play.sbs = SBs
						play.runs = RUNs
						play.slug = 0
						play.ptsabs = 0
						play.maxgame = maxgame
					else:
						play = PlayerStat(uid = user, name = name, pos = i, posstr = positions[i], espnid = espnid, teamid = teamid, teamname = teams.team[int(teamid)], bbcid = bbcid, abs = ABs, tbs = TBs, rbis = RBIs, bbs = BBs, sbs = SBs, runs = RUNs, slug = 0, ptsabs = 0, maxgame = maxgame)						
					play.save()
					#p = [name,positions[i],espnid,ABs,RUNs,TBs,RBIs,BBs,SBs,PTs]


		
		pe = PitcherEntry.objects.values('teamid').distinct().filter(entry__uid=user)
		for ti in pe:
			try:
				pitch = TeamPitcherStat.objects.get(uid = user, teamid = ti['teamid'])
				maxgamep = pitch.maxgame
				exists = True
			except ObjectDoesNotExist:
				maxgamep = 0
				exists = False
			#not sure if needed

			if maxgamep <= maxgame:
				
				teamid = ti['teamid']
				ps = PitcherEntry.objects.filter(entry__uid=user).filter(teamid=teamid)
				ip = 0
				name = ""
				for p in ps:
					ip = addIP(p.ip,ip)
				
				for p in ps:
					teamname = p.teamname
					teamid = p.teamid
					print teamid
					print teamname
					break
				
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
				
				
				if exists:
					pitch.hits = hits
					pitch.ers = ers
					pitch.bbs = bbs
					pitch.ks = ks
					pitch.pts = pts
					play.maxgame = maxgame
				else:
					pitch = TeamPitcherStat(uid = user, teamname = teamname, teamid = teamid, ips = ip, phits = hits, pbbs = bbs, ers = ers, ks = ks, ws = w, era = 0, whip = 0, maxgame = maxgame)
				pitch.save()
			
		
		pe = PitcherEntry.objects.values('espnid').distinct().filter(entry__uid=user)
		for es in pe:
			try:
				pitch = PitcherStat.objects.get(uid = user, espnid = es['espnid'])
				maxgamep = pitch.maxgame
				exists = True
			except ObjectDoesNotExist:
				maxgamep = 0
				exists = False
			#not sure if needed

			if maxgamep <= maxgame:
				
				espnid = es['espnid']
				ps = PitcherEntry.objects.filter(entry__uid=user).filter(espnid=espnid)
				ip = 0
				name = ""
				for p in ps:
					ip = addIP(p.ip,ip)
				
				for p in ps:
					teamname = p.teamname
					teamid = p.teamid
					espnid = p.espnid
					break
				
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
				
				
				if exists:
					pitch.hits = hits
					pitch.ers = ers
					pitch.bbs = bbs
					pitch.ks = ks
					pitch.pts = pts
					play.maxgame = maxgame
				else:
					pitch = PitcherStat(uid = user, espnid = espnid, teamname = teamname, teamid = teamid, ips = ip, phits = hits, pbbs = bbs, ers = ers, ks = ks, ws = w, era = 0, whip = 0, maxgame = maxgame)
				pitch.save()

		for i in range(0,9):
			c['totals'][positions[i]] = []
		
			pe = PlayerEntry.objects.filter(entry__uid=user).filter(pos=positions[i])
			#print str(t2-t1) + "    totals"
			peagg = pe.aggregate(Sum('abs'),Sum('tbs'),Sum('runs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('pts'))
		
			ABs = peagg['abs__sum']
			RUNs = peagg['runs__sum']
			TBs = peagg['tbs__sum']
			RBIs = peagg['rbis__sum']
			BBs = peagg['bbs__sum']
			SBs = peagg['sbs__sum']
			PTs = peagg['pts__sum']
			#salary = peagg['salary__avg']
			#ptspersalary = round(float(PTs)/salary,3)
			p = [positionstr[i],positions[i],"",ABs,RUNs,TBs,RBIs,BBs,SBs,PTs]
			#####
			pos = PositionPlayerStats(uid = user, pos = i, posstr = positions[i], posfullstr = positionstr[i], abs = ABs, tbs = TBs, rbis = RBIs, bbs = BBs, sbs = SBs, runs = RUNs, slug = 0, ptsabs = 0, maxgame = maxgame)
			pos.save()
			c['totals'][positions[i]].append(p)
	#print c['totals']
	for i in range(0,9):
		c[positions[i]] = PlayerStat.objects.filter(uid=user, pos = i)
		c['totals'][positions[i]] = PositionPlayerStats.objects.get(uid = user, pos = i)
	
	c['ptotals'] = TotalStats.objects.get(uid=user)
	c['pitchers'] = TotalTeamStats.objects.filter(uid=user)
	#for posi in range (0,9):
	#	c[positions[posi]] = sorted(c[positions[posi]], key=lambda p: p[3], reverse=True)
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
				print e.gamenumber
				prev = Entry.objects.get(uid=user,gamenumber = e.gamenumber-1)
				prevplayers = prev.players.all()
				prevpitcher = prev.pitchers.all()
				for p in e.players.all():
					position = p.pos
					#print p.name
					prevpos = prevplayers.get(pos=position)
					#print prevpos.name
					if not (prevpos.espnid == p.espnid):
						print position
						if position =="C":
							prevsalary = prev.p1salary
							newsalary = e.p1salary
						if position =="1B":
							prevsalary = prev.p2salary
							newsalary = e.p2salary						
						if position =="2B":
							prevsalary = prev.p3salary
							newsalary = e.p3salary
						if position =="3B":
							prevsalary = prev.p4salary
							newsalary = e.p4salary
						if position =="SS":
							prevsalary = prev.p5salary
							newsalary = e.p5salary
						if position =="LF":
							prevsalary = prev.p6salary
							newsalary = e.p6salary
						if position =="CF":
							prevsalary = prev.p7salary
							newsalary = e.p7salary
						if position =="RF":
							prevsalary = prev.p8salary
							newsalary = e.p8salary
						if position =="DH":
							prevsalary = prev.p9salary
							newsalary = e.p9salary
						log = UserTransactionLog.objects.get_or_create(uid=user,dropped=prevpos.name,droppedat=prevsalary,added=p.name,addedat=newsalary,gamenumber=e.gamenumber)
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
	tt = time.time()
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
	end = 138
	#print end
	for day in range(max,end+1):
		t1 = time.time()
		key = id * 1000000 + day
		try:
		    ent = Entry.objects.get(eid=key)
		except ObjectDoesNotExist:
			player = parser(id,day)
			if player == 0:
				return 
			tpts = 0
			if player != None:
				
				ent = Entry(eid=key,uid=user,gamenumber=day,points=0)
				abs = 0;tbs = 0;runs = 0;rbis = 0;bbs = 0;sbs = 0
				ips = 0;phits = 0;pbbs = 0;ers = 0;ks = 0;ws = 0
				pp=list()
				for i in player:
					if 'TB' in i:
						key = int(i['espnid']) * 1000000 + day
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
							pl = PlayerEntry(pid=key,espnid=i['espnid'],gamenumber=int(day),pos=i['pos'],bbcid=i['id'],doubleheader=i['dh'],nogame=i['nogame'],abs=i['AB'],runs=i['R'],tbs=i['TB'],rbis=i['RBI'],bbs=i['BB'],sbs=i['SB'],pts=pts,salary=i['salary'],teamid=i['teamid'],teamname=teams.team[int(i['teamid'])],name = i['FN'] + " " + i['LN'])
							#print "not created"
							pl.save()
							pp.append(pl)
					
					if 'IP' in i:
						key = int(i['teamid']) * 1000000 + day
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
							pi = PitcherEntry(pid=key,name = name, ip = i['IP'], gamenumber=int(day), espnid = i['id'], espnid2 = i['id2'], doubleheader = i['dh'], nogame = i['nogame'], hits = i['H'], ers = i['ER'], bbs = i['BB'], ks = i['K'], w = i['W'], pts = pts, salary =i['salary'], teamid =i['teamid'], teamname=teams.team[int(i['teamid'])])
							pi.save()
						ent.pitchers.add(pi)
				ent.players.add(*pp)				
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
			t2 = time.time()
			print str(t2 - t1) + " day " + str(day) 
		if day==end:
			print "end"
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
	tf = time.time()
	print tf-tt

	
def getDataNew(id):
	tt = time.time()
	file = "/Users/Jason/bbcdata/entrysqlnew" + ".db"
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
	end = 138
	for day in range(1,end+1):
		#print day
		key = id * 1000000 + day
		try:
			ent = Entry.objects.get(eid=key)
			print "day exists"
		except ObjectDoesNotExist:
			key = id * 1000000 + day
			c.execute("SELECT * FROM entry WHERE id = ?", (key,))
			e = c.fetchone()
			if e[3]=="True":
				
				ent = Entry(eid=key,uid=user,gamenumber=day,points=0)
				tpts = 0
				abs = 0;tbs = 0;runs = 0;rbis = 0;bbs = 0;sbs = 0
				ips = 0;phits = 0;pbbs = 0;ers = 0;ks = 0;ws = 0
			
				#player = parser(id,day)
				pp=list()
				sal=list()
				for i in range(4,21):
					if  i%2==0:			
						key = e[i] * 1000000 + day
						c.execute("SELECT * FROM player WHERE id = ?", (key,))
						p = c.fetchone()
						sal.append(p[8])
						pts = int(p[11]) + int(p[12]) + int(p[13]) + int(p[14]) + int(p[15])
						abs += int(p[10])
						tbs += int(p[15])
						runs += int(p[12])
						rbis += int(p[13])
						bbs += int(p[11])
						sbs += int(p[14])
						tpts += pts
						
						try:
							pl = PlayerEntry.objects.get(pid=key)							
						except ObjectDoesNotExist:
							pl = PlayerEntry(pid=key,espnid=p[5],gamenumber=int(day),pos=p[2],bbcid=p[6],doubleheader=p[16],nogame=p[18],abs=p[10],runs=p[12],tbs=p[15],rbis=p[13],bbs=p[11],sbs=p[14],pts=pts,teamid=p[7],teamname=teams.team[int(p[7])],name = p[3] + " " + p[4])
							pl.save()
						pp.append(pl)	
				ent.players.add(*pp)
				
				ent.p1salary=sal[0]
				ent.p2salary=sal[1]
				ent.p3salary=sal[2]
				ent.p4salary=sal[3]
				ent.p5salary=sal[4]
				ent.p6salary=sal[5]
				ent.p7salary=sal[6]
				ent.p8salary=sal[7]																				
				ent.p9salary=sal[8]
				
				key = e[22] * 1000000 + day
				c.execute("SELECT * FROM ps WHERE id = ?", (key,))
				ps = c.fetchone()
				#ipfrac = int(round((float(ps[13])-round(float(ps[13])))*10,0))
				#ip = round(float(ps[13]))*3+ipfrac
				ips = addIP(ips,float(ps[13]))
				phits += int(ps[14])
				pbbs += int(ps[16])
				ers += int(ps[15])
				ks += int(ps[17])
				ws += int(ps[18])
				pts = ipToOuts(ps[13]) + int(ps[17]) - int(ps[14]) - (3*int(ps[15])) - int(ps[16]) + (5*(int(ps[18])))
				tpts += pts
				try:
					pi = PitcherEntry.objects.get(pid=key)
				except ObjectDoesNotExist:
					name = teams.team[int(ps[11])]
					pi = PitcherEntry(pid=key,name = name, ip = ps[13], gamenumber=int(day), espnid = ps[8], espnid2 = ps[9], doubleheader = ps[19], nogame = ps[21], hits = ps[14], ers = ps[15], bbs = ps[16], ks = ps[17], w = ps[18], pts = pts, teamid = ps[10], teamname=teams.team[int(ps[10])])
					pi.save()
				ent.pitchers.add(pi)
				ent.pssalary=ps[13]
				
				ent.abs = abs
				ent.tbs = tbs
				ent.runs = runs
			
				ent.rbis = rbis
				ent.bbs = bbs
				ent.sbs = sbs
			
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
				#t2 = time.time()
				#print str(t2 - t1) + " day " + str(day)
		if day==end:
			user.maxgame = end
			user.totalpoints = utpts
			user.save()
			
			for i in range(1,30):
				totalStatsTeamUpdater(user,i,end)
	#print "stats done"
	#print user.name
			totalStatsUpdater(user,end)
	
	#pl = PlayerEntry.objects.all()
	#print pl.count()
	#pi = PitcherEntry.objects.all()
	#print pi.count()
	tf = time.time()
	print tf-tt



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
	file = "/Users/Jason/entries.txt"
	infile = open(file,"r")
	i = infile.readlines()
	for x in i:
		if x != "entries.txt":
			t1 = time.time()
			id = int(x.split("\n")[0])
			print id
			getDataNew(id)
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
	#print str(t2 - t1) + " day " + str(day) 
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
