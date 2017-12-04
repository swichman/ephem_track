# ephem_track
![Alt text](/resources/ephem_track.png?raw=true "Screenshot")
Small python program with gui to track satellites using TLE data from the web.

The usage is straight forward, and the program will save the TLE data to the local drive.

to run:
$./run.sh

-----------------------------------------------------------------------------------------
This script will check for the requisite libraries and inform you of what libraries are
not present for python.

As the satellite family is selected, the TLE's are downloaded from the internet. Once
the TLE files are generated, they will remain cached and usable while offline. Since
TLE's are only good for a couple of weeks, it's recommended that you ensure that you have
a fresh copy. To refresh the TLE's to what's available online, simple click the UpdateTLE
button for each family of satellites you are interested in having that information for.


