from django.db import models

# Create your models here.

class User (models.Model):
	uid = models.AutoField(primary_key=True)
	name  = models.CharField(max_length=128)
	espnid = models.IntegerField()
	totalpoints = models.IntegerField(null = True, blank = True)

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
	Ks = models.IntegerField(null = True, blank = True)
	Ws = models.IntegerField(null = True, blank = True)
	era = models.FloatField(null = True, blank = True)

class TotalStats(models.Model):
	uid = models.ForeignKey(User)
	tid = models.AutoField(primary_key=True)
	
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

class PitcherEntry(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	espnid = models.IntegerField()
	espnid2 = models.IntegerField()
	IP = models.FloatField()
	HITs = models.IntegerField()
	ERs = models.IntegerField()
	BBs = models.IntegerField()
	Ks = models.IntegerField()
	W = models.IntegerField()
	PTs = models.IntegerField()
	salary = models.FloatField()

class PlayerEntry(models.Model):
	pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length=128)
	Position = models.CharField(max_length=128)
	espnid = models.IntegerField()
	ABs = models.IntegerField()
	RUNs = models.IntegerField()
	TBs = models.IntegerField()
	RBIs = models.IntegerField()
	BBs = models.IntegerField()
	SBs = models.IntegerField()
	PTs = models.IntegerField()
	salary = models.FloatField()

class Entry(models.Model):
	uid = models.ForeignKey(User)
	eid = models.AutoField(primary_key=True)
	gamenumber = models.IntegerField()
	points = models.IntegerField()
	players = models.ManyToManyField(PlayerEntry)
	pitchers = models.ManyToManyField(PitcherEntry)