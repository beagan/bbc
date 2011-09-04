from django.db import models

class User (models.Model):
	uid = models.AutoField(primary_key=True)
	name  = models.CharField(max_length=128)
	espnid = models.IntegerField()
	totalpoints = models.IntegerField(null = True, blank = True)
	maxgame = models.IntegerField(null = True)


class UserRank(models.Model):
	uid = models.ForeignKey(User)
	date = models.DateField()
	rank = models.CharField(max_length=30)
	pct = models.CharField(max_length=30)


class UserTransactionLog(models.Model):
	uid = models.ForeignKey(User)
	dropped = models.CharField(max_length=500)
	droppedat = models.FloatField()
	added = models.CharField(max_length=500)
	addedat = models.FloatField()
	gamenumber = models.IntegerField()


class UserStats(models.Model):
	uid = models.ForeignKey(User)
	usid = models.AutoField(primary_key=True)
	game = models.IntegerField()
	
	abs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	slug = models.FloatField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	era = models.FloatField(null = True, blank = True)
	points = models.IntegerField(null = True, blank = True)
	
	runwin = models.IntegerField(default = 0)
	runloss = models.IntegerField(default = 0)
	runtie = models.IntegerField(default = 0)
	
	rbiwin = models.IntegerField(default = 0)
	rbiloss = models.IntegerField(default = 0)
	rbitie = models.IntegerField(default = 0)
	
	ptsabs = models.FloatField(null = True, blank = True)	


class TotalStats(models.Model):
	uid = models.ForeignKey(User)
	tid = models.AutoField(primary_key=True)
	
	maxgame = models.IntegerField(null = True, blank = True)
	
	abs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	slug = models.FloatField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	
	era = models.FloatField(null = True, blank = True)
	whip = models.FloatField(null = True, blank = True)
	
	playpoints = models.IntegerField(null = True, blank = True)
	pitchpoints = models.IntegerField(null = True, blank = True)
	
	points = models.IntegerField(null = True, blank = True)
	
	runwin = models.IntegerField(default = 0,null = True, blank = True)
	runloss = models.IntegerField(default = 0,null = True, blank = True)
	runtie = models.IntegerField(default = 0,null = True, blank = True)
	
	rbiwin = models.IntegerField(default = 0,null = True, blank = True)
	rbiloss = models.IntegerField(default = 0,null = True, blank = True)
	rbitie = models.IntegerField(default = 0,null = True, blank = True)
	
	ptsabs = models.FloatField(null = True, blank = True)


class TotalTeamStats(models.Model):
	uid = models.ForeignKey(User)
	tid = models.AutoField(primary_key=True)
	
	teamid = models.IntegerField()
	teamname = models.CharField(max_length=128)
	
	maxgame = models.IntegerField(null = True, blank = True)
	
	abs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	slug = models.FloatField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	
	era = models.FloatField(null = True, blank = True)
	whip = models.FloatField(null = True, blank = True)
	
	playpoints = models.IntegerField(null = True, blank = True)
	pitchpoints = models.IntegerField(null = True, blank = True)
	
	points = models.IntegerField(null = True, blank = True)
	
	playspresent = models.BooleanField(null = False, blank = False)
	pitspresent = models.BooleanField(null = False, blank = False)
	
	ptsabs = models.FloatField(null = True, blank = True)


class PitcherEntry(models.Model):
	pid = models.BigIntegerField(primary_key=True)
	name = models.CharField(max_length=128)
	gamenumber = models.IntegerField()
	espnid = models.IntegerField()
	espnid2 = models.IntegerField()
	teamid = models.IntegerField()
	teamname = models.CharField(max_length=128)
	doubleheader = models.BooleanField()
	nogame = models.BooleanField()
	ip = models.FloatField()
	hits = models.IntegerField()
	ers = models.IntegerField()
	bbs = models.IntegerField()
	ks = models.IntegerField()
	w = models.IntegerField()
	pts = models.IntegerField()


class PlayerEntry(models.Model):
	pid = models.BigIntegerField(primary_key=True)
	name = models.CharField(max_length=128,null = True, blank = True)
	gamenumber = models.IntegerField()
	pos = models.CharField(max_length=128,null = True, blank = True)
	espnid = models.IntegerField()
	bbcid = models.IntegerField(null = True, blank = True)
	teamid = models.IntegerField(null = True, blank = True)
	teamname = models.CharField(max_length=128)
	doubleheader = models.BooleanField(default = True, blank = True)
	nogame = models.BooleanField(default = True, blank = True)
	abs = models.IntegerField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	pts = models.IntegerField(null = True, blank = True)


class Entry(models.Model):
	uid = models.ForeignKey(User)
	eid = models.BigIntegerField(primary_key=True)
	gamenumber = models.IntegerField()
	points = models.IntegerField()
	players = models.ManyToManyField(PlayerEntry)
	pitchers = models.ManyToManyField(PitcherEntry)
	
	p1salary = models.FloatField(null = True, blank = True)
	p2salary = models.FloatField(null = True, blank = True)
	p3salary = models.FloatField(null = True, blank = True)
	p4salary = models.FloatField(null = True, blank = True)
	p5salary = models.FloatField(null = True, blank = True)
	p6salary = models.FloatField(null = True, blank = True)
	p7salary = models.FloatField(null = True, blank = True)
	p8salary = models.FloatField(null = True, blank = True)
	p9salary = models.FloatField(null = True, blank = True)							
	pssalary = models.FloatField(null = True, blank = True)
	
	abs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	
	slug = models.FloatField(null = True, blank = True)
	era = models.FloatField(null = True, blank = True)
	whip = models.FloatField(null = True, blank = True)
	
	runwin = models.IntegerField(default = 0,null = True, blank = True)
	runloss = models.IntegerField(default = 0,null = True, blank = True)
	runtie = models.IntegerField(default = 0,null = True, blank = True)
	
	rbiwin = models.IntegerField(default = 0,null = True, blank = True)
	rbiloss = models.IntegerField(default = 0,null = True, blank = True)
	rbitie = models.IntegerField(default = 0,null = True, blank = True)
	
	ptsabs = models.FloatField(null = True, blank = True)


class PositionPlayerStats(models.Model):
	uid = models.ForeignKey(User)
	pid = models.AutoField(primary_key =True)
	
	pos = models.IntegerField()
	posstr = models.CharField(max_length=3)
	posfullstr = models.CharField(max_length=128)
	
	abs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	
	slug = models.FloatField(null = True, blank = True)
	ptsabs = models.FloatField(null = True, blank = True)
	
	pts = models.IntegerField(null = True, blank = True)
	
#	players = models.ManyToManyField(PlayerStatEntry)
	maxgame = models.IntegerField(null = True, blank = True)


class PositionPitcherStats(models.Model):
	uid = models.ForeignKey(User)
	pid = models.AutoField(primary_key =True)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	
	era = models.FloatField(null = True, blank = True)
	whip = models.FloatField(null = True, blank = True)
	
	#pitchers = models.ManyToManyField(PitcherStat)
	maxgame = models.IntegerField(null = True, blank = True)


class PlayerStat(models.Model):
	uid = models.ForeignKey(User)
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128,null = True, blank = True)
	#include array,manytomany?gamenumbers
	pos = models.IntegerField(null = True, blank = True, db_index = True)
	posstr = models.CharField(max_length=128,null = True, blank = True)
	espnid = models.IntegerField()
	bbcid = models.IntegerField(null = True, blank = True)
	teamid = models.IntegerField(null = True, blank = True)
	teamname = models.CharField(null = True, blank = True, max_length=128)
	
	abs = models.IntegerField(null = True, blank = True)
	tbs = models.IntegerField(null = True, blank = True)
	rbis = models.IntegerField(null = True, blank = True)
	bbs = models.IntegerField(null = True, blank = True)
	sbs = models.IntegerField(null = True, blank = True)
	runs = models.IntegerField(null = True, blank = True)
	
	slug = models.FloatField(null = True, blank = True)
	ptsabs = models.FloatField(null = True, blank = True)
	
	maxgame = models.IntegerField(null = True, blank = True)
	
	pts = models.IntegerField(null = True, blank = True)


class PitcherStat(models.Model):
	uid = models.ForeignKey(User)
	pid = models.AutoField(primary_key =True)
	
	teamid = models.IntegerField(null = True, blank = True)
	teamname = models.CharField(null = True, blank = True, max_length=128)
	
	espnid = models.IntegerField(null = True, blank = True)
	name = models.IntegerField(null = True, blank = True)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	
	era = models.FloatField(null = True, blank = True)
	whip = models.FloatField(null = True, blank = True)
	
	maxgame = models.IntegerField(null = True, blank = True)


class TeamPitcherStat(models.Model):
	uid = models.ForeignKey(User)
	pid = models.AutoField(primary_key =True)
	
	teamid = models.IntegerField(null = True, blank = True)
	teamname = models.CharField(null = True, blank = True, max_length=128)
	
	ips = models.FloatField(null = True, blank = True)
	phits = models.IntegerField(null = True, blank = True)
	pbbs = models.IntegerField(null = True, blank = True)
	ers = models.IntegerField(null = True, blank = True)
	ks = models.IntegerField(null = True, blank = True)
	ws = models.IntegerField(null = True, blank = True)
	
	era = models.FloatField(null = True, blank = True)
	whip = models.FloatField(null = True, blank = True)
	
	maxgame = models.IntegerField(null = True, blank = True)


class Lineup(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128,null = True, blank = True)
	catcher = models.CharField(max_length=128,null = True, blank = True)
	catchername = models.CharField(max_length=128,null = True, blank = True)
	firstbase = models.CharField(max_length=128,null = True, blank = True)
	firstbasename = models.CharField(max_length=128,null = True, blank = True)
	secondbase = models.CharField(max_length=128,null = True, blank = True)
	secondbasename = models.CharField(max_length=128,null = True, blank = True)
	thirdbase = models.CharField(max_length=128,null = True, blank = True)
	thirdbasename = models.CharField(max_length=128,null = True, blank = True)
	shortstop = models.CharField(max_length=128,null = True, blank = True)
	shortstopname = models.CharField(max_length=128,null = True, blank = True)
	leftfield = models.CharField(max_length=128,null = True, blank = True)
	leftfieldname = models.CharField(max_length=128,null = True, blank = True)
	centerfield = models.CharField(max_length=128,null = True, blank = True)
	centerfieldname = models.CharField(max_length=128,null = True, blank = True)
	rightfield = models.CharField(max_length=128,null = True, blank = True)
	rightfieldname = models.CharField(max_length=128,null = True, blank = True)
	dh = models.CharField(max_length=128,null = True, blank = True)
	dhname = models.CharField(max_length=128,null = True, blank = True)
	ps = models.CharField(max_length=128,null = True, blank = True)
	psname = models.CharField(max_length=128,null = True, blank = True)

	
class Top100Lineup(models.Model):
	id = models.AutoField(primary_key=True)
	top100 = models.ManyToManyField(Lineup)
	date = models.DateField()
