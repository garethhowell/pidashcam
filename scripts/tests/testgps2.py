import gps

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True:
    try:
    	report = session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
        #print report
        if report['class'] == 'TPV':
            print report
            if hasattr(report, 'time'):
                print report.time
            if hasattr(report, 'lat'):
                print report.lat
            if hasattr(report, 'lon'):
                print report.lon
            print(report.time + " " + report.lat + " " + report.lon)

    except KeyError:
		pass
    except KeyboardInterrupt:
		quit()
    except StopIteration:
		session = None
		print "GPSD has terminated"
