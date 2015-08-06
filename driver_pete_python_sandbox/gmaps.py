# ============================================================================
# Copyright 2014 BRAIN Corporation. All rights reserved. This software is
# provided to you under BRAIN Corporation's Beta License Agreement and
# your use of the software is governed by the terms of that Beta License
# Agreement, found at http://www.braincorporation.com/betalicense.
# ============================================================================


import cv2
import urllib
import numpy as np
from geopy.geocoders import GoogleV3 as Geocoder
from matplotlib.dates import datestr2num, num2date
import matplotlib.pyplot as plots


def get_static_google_map(center=None, zoom=12, imgsize=(500, 500), imgformat="jpg",
                          maptype="roadmap", markers=None):  
    """retrieve a map (image) from the static google maps server 
    
     See: http://code.google.com/apis/maps/documentation/staticmaps/
        
        Creates a request string with a URL like this:
        http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=roadmap
&markers=color:blue|label:S|40.702147,-74.015794&sensor=false
    """

    # assemble the URL
    request = "http://maps.google.com/maps/api/staticmap?"  # base URL, append query params, separated by &
   
    # if center and zoom  are not given, the map will show all marker locations
    if center is not None:
        if isinstance(center, str):
            request += "center=%s&" % (center,)
        elif isinstance(center, int):
            request += "center=%d&" % (center,)
        else:
            request += "center=%f, %f&" % tuple(center)
    if zoom is not None:
        request += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)

    request += "size=%ix%i&" % (imgsize)  # tuple of ints, up to 640 by 640
    request += "format=%s&" % imgformat

    assert(maptype in ['roadmap', 'satelite', 'hybrid', 'terrain'])
    request += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain

    # add markers (location and style)
    if markers is not None:
        marker_str = "markers=color:red|size:tiny|"
        for m in markers:
            marker_str += '%f %f|' % tuple(m)
        marker_str += "&"
        request += marker_str

    # request += "mobile=false&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
    request += "sensor=false&"   # must be given, deals with getting location from mobile device 
    
    print("Issuing request %s" % request)
    web_sock = urllib.urlopen(request)
    code = web_sock.getcode()
    if code != 200:
        raise Exception(web_sock.read())
    
    imgdata = web_sock.read()
    picture = cv2.imdecode(np.frombuffer(imgdata, np.uint8), 1)    
    return picture


def trajectory_point_to_str(data, index):
    geocoder = Geocoder()
    request = "%s, %s" % tuple(data[index][1:])
    address = geocoder.reverse(request, exactly_one = True).address
    date = num2date(data[index][0])
    try:
        duration = num2date(data[index+1][0]) - date
    except IndexError:
        duration = "NO DATA"
    return "Index:%s; Date:%s; Address:%s; Coords: %s; Duration:%s;" % \
        (index, date, request, address, duration)


def show_path(data, path_indices):
    path = data[path_indices[0]:path_indices[1]+1, :]
    times, coordinates = path[:, 0], path[:, 1:]
    
    center = np.average(coordinates, axis=0)
 
    max_markers = 64
    for i in range(len(coordinates)/max_markers + 1):
        imgdata = get_static_google_map(
            markers=coordinates[i*max_markers:(i+1)*max_markers]
            # center=center,
            # zoom=11,
        )
     
        cv2.imshow(str(i), imgdata)
    cv2.waitKey()
     
    plots.plot(coordinates[:, 0], coordinates[:, 1], 'ro')
    plots.show()
