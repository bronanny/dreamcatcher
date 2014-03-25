Dreamcatcher
============

Simple monitoring system.  Uses Statsd, Hekad, Whisper (from Graphite), and D3.js.  Aims to be simple and easy to deploy.

Why?
------------

I wanted a very simple system that would monitor and record stats and show me informative and reasonably good looking graphs and charts.  I didn't find anything quite to my liking, although there were parts of existing systems that seemed pretty good (Statd, Whisper database, Heka project.)

After spending several days searching and reading I realized that by the time I learned how to install and configure e.g. Graphite I might as well just write a quick "80% solution".

License
------------

The files ``whisper.py`` and ``statsd.py`` are under their own licences.  The rest of this code is released under the GPLv3, see ``LICENSE``.

What & How?
------------

The idea is simple: You collect stats and send them to a Hekad instance that records them in the whisper database.  The "whisper server" serves a snapshot of the data and a D3.js-powered introspection tool for it.  It's somewhat crude but it seems to work really well for small-ish data and usage.  It's small and easy to understand and deploy.

The Hekad config file simply sets up a very simple statsd-to-whisper pipeline.  It listens for UDP statsd packets and writes out a whisper database.

Hekad has a lot of other capabilities including filters and such written in Lua (and there's a PEG parser for Lua, so... wow.  Much power.)  We're not taking advantage of any of that really.  I have high hopes for the Heka project.

The mongotop statsd script takes in the output of mongotop and sends UDP statsd messages to a listener.

The ``whisper_server.py`` script is a first draft of a very simple way to access and graph the stats in a whisper database.  Right now it simply loads all the data in a given whisper directory and converts it to JSON representation.  It then serves the JSON at URLs given by the (dotted) name of the stat.  It also serves the static content of a single-page web "app" that uses D3.js to generate nice charts and graphs, fetching stat data from the server via AJAX requests.

Running
------------

* Download Hekad
* Run whatever statsd reporting scripts, point them at Hekad
* Run the whisper server and point it at the whisper dir
    * for the moment you've got to restart it to reload the data...
    * it's basically a proof of concept prototype.
