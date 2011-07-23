from django.db import models

# Create your models here.

class User (models.Model):
	uid = models.AutoField(primary_key=True)
	name  = models.CharField(max_length=128)
	espnid = models.IntegerField()
	totalpoints = models.IntegerField(null = True, blank = True)

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

class UserStats(models.Model):
	uid = models.ForeignKey(User)
	usid = models.AutoField(primary_key=True)
	game = models.IntegerField()

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
	Ks = models.IntegerField(null = True, blank = True)
	Ws = models.IntegerField(null = True, blank = True)

	slug = models.FloatField(null = True, blank = True)
	era = models.FloatField(null = True, blank = True)
	runwin = models.IntegerField(null = True, blank = True)
	rbiwin = models.IntegerField(null = True, blank = True)
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
	Ks = models.IntegerField(null = True, blank = True)
	Ws = models.IntegerField(null = True, blank = True)
	era = models.FloatField(null = True, blank = True)
	points = models.IntegerField(null = True, blank = True)

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
	Ks = models.IntegerField(null = True, blank = True)
	Ws = models.IntegerField(null = True, blank = True)
	era = models.FloatField(null = True, blank = True)
	points = models.IntegerField(null = True, blank = True)

	ptsabs = models.FloatField(null = True, blank = True)

class PitcherEntry(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	espnid = models.IntegerField()
	espnid2 = models.IntegerField()
	teamid = models.IntegerField()
	teamname = models.CharField(max_length=128)
	doubleheader = models.BooleanField()
	ip = models.FloatField()
	hits = models.IntegerField()
	ers = models.IntegerField()
	bbs = models.IntegerField()
	ks = models.IntegerField()
	w = models.IntegerField()
	pts = models.IntegerField()
	salary = models.FloatField()

class PlayerEntry(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	pos = models.CharField(max_length=128)
	espnid = models.IntegerField()
	bbcid = models.IntegerField()
	teamid = models.IntegerField()
	teamname = models.CharField(max_length=128)
	doubleheader = models.BooleanField()
	abs = models.IntegerField()
	runs = models.IntegerField()
	tbs = models.IntegerField()
	rbis = models.IntegerField()
	bbs = models.IntegerField()
	sbs = models.IntegerField()
	pts = models.IntegerField()
	salary = models.FloatField()

class Entry(models.Model):
	uid = models.ForeignKey(User)
	eid = models.AutoField(primary_key=True)
	gamenumber = models.IntegerField()
	points = models.IntegerField()
	players = models.ManyToManyField(PlayerEntry)
	pitchers = models.ManyToManyField(PitcherEntry)

class Lineup(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128,null = True, blank = True)
	catcher = models.CharField(max_length=128,null = True, blank = True)
	firstbase = models.CharField(max_length=128,null = True, blank = True)
	secondbase = models.CharField(max_length=128,null = True, blank = True)
	thirdbase = models.CharField(max_length=128,null = True, blank = True)
	shortstop = models.CharField(max_length=128,null = True, blank = True)
	leftfield = models.CharField(max_length=128,null = True, blank = True)
	centerfield = models.CharField(max_length=128,null = True, blank = True)
	rightfield = models.CharField(max_length=128,null = True, blank = True)
	dh = models.CharField(max_length=128,null = True, blank = True)
	ps = models.CharField(max_length=128,null = True, blank = True)
	
class Top100Lineup(models.Model):
	id = models.AutoField(primary_key=True)
	top100 = models.ManyToManyField(Lineup)
	date = models.DateField()

