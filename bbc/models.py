from django.db import models

# Create your models here.

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
	points = models.IntegerField(null = True, blank = True)
	
	runwin = models.IntegerField(default = 0)
	runloss = models.IntegerField(default = 0)
	runtie = models.IntegerField(default = 0)
	
	rbiwin = models.IntegerField(default = 0)
	rbiloss = models.IntegerField(default = 0)
	rbitie = models.IntegerField(default = 0)
	
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
	points = models.IntegerField(null = True, blank = True)

	ptsabs = models.FloatField(null = True, blank = True)

class PitcherEntry(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	gamenumber = models.IntegerField(db_index = True)
	espnid = models.IntegerField()
	espnid2 = models.IntegerField()
	teamid = models.IntegerField(db_index = True)
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
	salary = models.FloatField()

class PlayerEntry(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128,null = True, blank = True)
	gamenumber = models.IntegerField(db_index = True)
	pos = models.CharField(max_length=128,null = True, blank = True)
	espnid = models.IntegerField(db_index = True)
	bbcid = models.IntegerField(null = True, blank = True)
	teamid = models.IntegerField(null = True, blank = True, db_index = True)
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
	salary = models.FloatField(null = True, blank = True)


class Entry(models.Model):
	uid = models.ForeignKey(User)
	eid = models.AutoField(primary_key=True)
	gamenumber = models.IntegerField(db_index=True)
	points = models.IntegerField()
	players = models.ManyToManyField(PlayerEntry)
	pitchers = models.ManyToManyField(PitcherEntry)
	
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
	
	runwin = models.IntegerField(default = 0,null=False)
	runloss = models.IntegerField(default = 0,null=False)
	runtie = models.IntegerField(default = 0,null=False)
	
	rbiwin = models.IntegerField(default = 0,null=False)
	rbiloss = models.IntegerField(default = 0,null=False)
	rbitie = models.IntegerField(default = 0,null=False)
	
	ptsabs = models.FloatField(null = True, blank = True)

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

