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
	
	abs = models.IntegerField()
	tbs = models.IntegerField()
	rbis = models.IntegerField()
	bbs = models.IntegerField()
	sbs = models.IntegerField()
	slug = models.FloatField()
	runs = models.IntegerField()
	
	ips = models.FloatField()
	phits = models.IntegerField()
	pbbs = models.IntegerField()
	ers = models.IntegerField()
	Ks = models.IntegerField()
	Ws = models.IntegerField()
	era = models.FloatField()

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

class Entry(models.Model):
	uid = models.ForeignKey(User)
	eid = models.AutoField(primary_key=True)
	gamenumber = models.IntegerField()
	points = models.IntegerField()
	players = models.ManyToManyField(PlayerEntry)
	pitchers = models.ManyToManyField(PitcherEntry)
		

