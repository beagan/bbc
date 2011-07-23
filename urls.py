from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    (r"^$", 'bbc.views.HomeHandler'),# 	url(r'^bbcstats/', include('bbcstats.foo.urls')),
	(r"^stats", 'bbc.views.StatsHandler'),
	(r"^posstats", 'bbc.views.PositionStatsHandler'),
	(r"^viewranks", 'bbc.views.viewRanks'),
	(r"^viewtop100", 'bbc.views.viewTop100Lineup'),
	#(r"^$", 'bbcstats.views.HomeHandler'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
	
)
