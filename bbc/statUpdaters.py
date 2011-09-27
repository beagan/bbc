from bbcstats.bbc.models import *
from django.db.models import Q, Max, Sum, Avg
import statTools
import teams

def totalStatsUpdater(user,maxgame):
	try:
		tot = TotalStats.objects.get(uid=user)
		if tot.maxgame >= maxgame:
			print "none"
			return
	except:
		x=1	
	entry = Entry.objects.filter(uid=user)
	
	agg = entry.all().aggregate(Sum('abs'),Sum('tbs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('runs'),Sum('phits'),Sum('pbbs'),Sum('ers'),Sum('ks'),Sum('ws'),Sum('rbiwin'),Sum('rbitie'),Sum('rbiloss'),Sum('runwin'),Sum('runtie'),Sum('runloss'),Sum('points'))
	totabs = agg['abs__sum']
	tottbs = agg['tbs__sum']
	totrbis = agg['rbis__sum']
	totbbs = agg['bbs__sum']
	totsbs = agg['sbs__sum']
	totruns = agg['runs__sum']
	ips=0
	for p in entry.all():
		ips = statTools.addIP(ips,p.ips)
	totips = ips
	totphits = agg['phits__sum']
	totpbbs = agg['pbbs__sum']
	toters = agg['ers__sum']
	totks = agg['ks__sum']
	totws = agg['ws__sum']
	
	totrunwin = agg['runwin__sum']
	totruntie = agg['runtie__sum']
	totrunloss = agg['runloss__sum']
	
		
	totrbiwin = agg['rbiwin__sum']
	totrbitie = agg['rbitie__sum']
	totrbiloss = agg['rbiloss__sum']
			
	if totabs > 0:
		totslug = float(agg['tbs__sum']) /float(agg['abs__sum'])
		totptsabs = float(agg['tbs__sum']+agg['runs__sum']+agg['rbis__sum']+agg['bbs__sum']+agg['sbs__sum'])/float(agg['abs__sum'])
	else:
		totslug = 0
		totptsabs = 0
	if toters > 0:
		totera = float(agg['ers__sum']*9)/(float(statTools.ipToOuts(totips))/3)
	else:
		totera = 0
	if totips > 0:
		totwhip = float(totphits+totpbbs)/(float(statTools.ipToOuts(totips))/3)
	else:
		totwhip = 0
	totplaypoints=0;totpitchpoints=0
	if totabs>0 or totbbs>0:
		totplaypoints = tottbs + totrbis + totbbs + totsbs + totruns
	if totips>0:
		totpitchpoints = statTools.ipToOuts(totips) - totphits -totpbbs - toters*3 + totks + totws*5
	
	
	pts = agg['points__sum']
	totpoints = pts
	
	totmaxgame = maxgame
	
	print user.name
	
	TotalStats.objects.bulk_insert(uid=user,abs=totabs,tbs=tottbs,rbis=totrbis,bbs=totbbs,sbs=totsbs,slug=totslug,runs=totruns,ips=totips,phits=totphits,pbbs=totpbbs,ers=toters,ks=totks,ws=totws,era=totera,whip=totwhip,playpoints=totplaypoints,pitchpoints=totpitchpoints,runwin=totrunwin,runloss=totrunloss,runtie=totruntie,rbiwin=totrbiwin,rbiloss=totrbiloss,rbitie=totrbitie,ptsabs=totabs,maxgame=maxgame)


def totalStatsTeamUpdater(user,maxgame):
	try:
		tot = TotalTeamStats.objects.get(uid=user,teamid=1)
		print "has it"
		if tot.maxgame >= maxgame:
			print "none team"
			return 1
	except:
		print "doesnt have it"
		x=1	
	pla = PlayerEntry.objects.filter(entry__uid=user).all()

	for i in range(1,30):
	
		plat = pla.filter(teamid=i)
		#placount = pla.count()
	
		pitpres = False
		plapres = False
	
		totabs=0;tottbs=0;totrbis=0;totbbs=0;totsbs=0;totruns=0;totslug=0;totptsabs=0
		
		#for p in pla.all():
		#	totabs += p.abs
		#	totrbis += p.tbs
		#	totbbs += p.bbs
		#	totsbs += p.sbs
		#	totruns += p.runs
		agg = plat.all().aggregate(Sum('abs'),Sum('tbs'),Sum('rbis'),Sum('bbs'),Sum('sbs'),Sum('runs'))
		totabs = agg['abs__sum']
		tottbs = agg['tbs__sum']
		totrbis = agg['rbis__sum']
		totbbs = agg['bbs__sum']
		totsbs = agg['sbs__sum']
		totruns = agg['runs__sum']

		if totabs > 0:
			totslug = float(tottbs) /float(totabs)
			totptsabs = float(tottbs+totruns+totrbis+totbbs+totsbs)/float(totabs)
		else:
			totslug = 0
			totptsabs = 0
		if totabs > 0 or totbbs > 0:
			plapres = True
	
		pit = PitcherEntry.objects.filter(teamid=i).filter(entry__uid=user)
		#pitcount = pit.count()
		totips = 0;totphits=0;totpbbs=0;toters=0;totks=0;totws=0;totera=0;totwhip=0

		for p in pit.all():
			totips = statTools.addIP(totips,p.ip)
			totphits += p.hits
			totpbbs += p.bbs
			toters += p.ers
			totks += p.ks
			totws += p.w
		#aggp = pit.all().aggregate(Sum('hits'),Sum('bbs'),Sum('ers'),Sum('ks'),Sum('w'))
		#totphits = aggp['hits__sum']
		#totpbbs = aggp['bbs__sum']
		#toters = aggp['ers__sum']
		#totks = aggp['ks__sum']
		#totws = aggp['w__sum']
		if toters > 0:
			totera = float(toters*9)/(float(statTools.ipToOuts(totips))/3)
		else:
			totera = 0
		if totips > 0:
			totwhip = float(totphits+totpbbs)/(float(statTools.ipToOuts(totips))/3)
		else:
			totwhip = 0
		if totips > 0 or totphits > 0 or totpbbs > 0:
			pitpres = True
		
		#count = int(placount) + int(pitcount)
		totplaypoints = 0
		totpitchpoints = 0
		totpoints = 0
		if pitpres or plapres:
			if plapres and pitpres:
				totplaypoints = tottbs + totrbis + totbbs + totsbs + totruns
				totpitchpoints = statTools.ipToOuts(totips) - totphits -totpbbs - toters*3 + totks + totws*5
				totpoints = totplaypoints + totpitchpoints
			else:
				if plapres:
					totplaypoints = tottbs + totrbis + totbbs + totsbs + totruns
					totpitchpoints = 0
					totpoints = totplaypoints + totpitchpoints
				else:
					if pitpres:
						totplaypoints = 0
						totpitchpoints = statTools.ipToOuts(totips) - totphits -totpbbs - toters*3 + totks + totws*5
						totpoints = totplaypoints + totpitchpoints
	

		#key = user.espnid * 10000 + teamid
		TotalTeamStats.objects.bulk_insert(uid=user,
										teamid=i,
										teamname=teams.team[int(i)],
										abs=totabs,
										tbs=tottbs,
										rbis=totrbis,
										bbs=totbbs,
										sbs=totsbs,
										slug=totslug,
										runs=totruns,
										ips=totips,
										phits=totphits,
										pbbs=totpbbs,
										ers=toters,
										ks=totks,
										ws=totws,
										era=totera,
										whip=totwhip,
										playpoints=totplaypoints,
										pitchpoints=totpitchpoints,
										points = totpoints,
										playspresent=plapres,
										pitspresent=pitpres,
										ptsabs=totabs,
										maxgame=maxgame)
	return 0
	#print tot