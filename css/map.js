rad = function(x) {return x*Math.PI/180;}

function distHaversine(p1, p2) {
  var R = 6371; // earth's mean radius in km
  var dLat  = rad(p2.lat() - p1.lat());
  var dLong = rad(p2.lng() - p1.lng());

  var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.cos(rad(p1.lat())) * Math.cos(rad(p2.lat())) * Math.sin(dLong/2) * Math.sin(dLong/2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  var d = R * c;

  return (d * 0.621371).toFixed(1);
}

function linkColor(link) {
    if (location.hostname == 'www.hamwan.org') {
        return link.STRENGTH && link.TYPE != 'SURVEY' ? '#0086db' : '#666';
    } else {
        return link.LINK_COLOR;
    }
}

function linkOpacity() {
    return location.hostname == 'www.hamwan.org' ? 0.5 : 0.7;
}

function linkWidth(link) {
    return (link.SPEED || 1000000) / 4000000 + 3
}

function initialize() {
    var sites = {
        1: {NAME: 'Capitol Park',
            position: new google.maps.LatLng(47.62378,-122.3152),
            icon: '//www.hamwan.org/t/tiki-download_wiki_attachment.php?attId=118'},
        2: {NAME: 'Paine',
            position: new google.maps.LatLng(47.92386,-122.2441),
            icon: '//www.hamwan.org/t/tiki-download_wiki_attachment.php?attId=118'},
        3: {NAME: 'Baldi',
            position: new google.maps.LatLng(47.219,-121.8432),
            icon: '//www.hamwan.org/t/tiki-download_wiki_attachment.php?attId=118'},
        4: {NAME: 'Mirrormont',
            position: new google.maps.LatLng(47.46228,-121.9742),
            icon: '//dl.dropboxusercontent.com/u/8174/sector3.png'},
        5: {NAME: 'Haystack',
            position: new google.maps.LatLng(47.8093,-121.7507),
            icon: '//dl.dropboxusercontent.com/u/8174/sector3.png'},
        6: {NAME: 'Westin',
            position: new google.maps.LatLng(47.6145,-122.3391),
            icon: '//upload.wikimedia.org/wikipedia/commons/8/8c/Transparent.png'}
    };
    var coverage = [
        {   NAME: 'first 3',
            src: '//dl.dropboxusercontent.com/u/8174/hamwancoverage.png',
            n: 48.34369, e: -121.6021, s: 46.90387, w: -123.0283},
        {   NAME: 'Mirrormont',
            src: '//dl.dropboxusercontent.com/u/8174/mirrormontcoverage.png',
            n: 47.89927, e: -121.5867, s: 46.63943, w: -123.0717},
        {   NAME: 'Haystack',
            src: '//dl.dropboxusercontent.com/u/8174/haystackcoverage.png',
            n: 48.43857, e: -121.4244, s: 47.17873, w: -122.9248}
        // {   NAME: 'Mile Hill S1',
        //     src: '//dl.dropboxusercontent.com/u/8174/milehillS1coverage.png',
        //     n: 48.06031, e: -121.9082, s: 47.3404, w: -123.335},
        // {   NAME: 'Mile Hill S2',
        //     src: '//dl.dropboxusercontent.com/u/8174/milehillS2coverage.png',
        //     n: 47.65501, e: -122.0908, s: 47.29505, w: -122.801}
    ];
    var mapOptions = {
        center: sites[1].position,
        zoom:  9,
        scrollwheel: location.hostname != 'www.hamwan.org',
        mapTypeId: google.maps.MapTypeId.TERRAIN,
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
        }
    };

    var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

    // Center map at browser location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            // Require coordinates in Puget Sound area
            if (position.coords.latitude >= 46.5 && position.coords.latitude < 48.5 &&
                position.coords.longitude >= -123.5 && position.coords.longitude < -121.5) {
                initialLocation = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                map.setCenter(initialLocation);
                map.setZoom(10);
            }
        });
    }

    // Set up search/autocomplete

    var input = /** @type {HTMLInputElement} */(document.getElementById('searchTextField'));
    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo('bounds', map);

    var infowindow = new google.maps.InfoWindow();
    var marker = new google.maps.Marker({
        map: map,
        anchorPoint: new google.maps.Point(0, -29)
    });

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
        infowindow.close();
        marker.setVisible(false);
        input.className = '';
        var place = autocomplete.getPlace();
        if (!place.geometry) {
          // Inform the user that the place was not found and return.
          input.className = 'notfound';
          return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
          map.fitBounds(place.geometry.viewport);
        } else {
          map.setCenter(place.geometry.location);
          map.setZoom(13);
        }
        marker.setIcon(/** @type {google.maps.Icon} */({
          url: place.icon,
          size: new google.maps.Size(71, 71),
          origin: new google.maps.Point(0, 0),
          anchor: new google.maps.Point(17, 34),
          scaledSize: new google.maps.Size(35, 35)
        }));
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);

        var address = '';
        if (place.address_components) {
          address = [
            (place.address_components[0] && place.address_components[0].short_name || ''),
            (place.address_components[1] && place.address_components[1].short_name || ''),
            (place.address_components[2] && place.address_components[2].short_name || '')
          ].join(' ');
        }

        infowindow.setContent('<div><strong>' + place.name + '</strong><br>' + address);
        infowindow.open(map, marker);
    });

    // Add coverage maps
    for (var i in coverage) {
        var overlay = coverage[i];
        var overlaybounds = new google.maps.LatLngBounds(
            new google.maps.LatLng( overlay.s, overlay.w),
            new google.maps.LatLng( overlay.n, overlay.e));
        var coveragemap = new google.maps.GroundOverlay(overlay.src,
            overlaybounds, {opacity:0.5});
        coveragemap.setMap(map);
    }

    // Get network status (site/clients/link data)
    $.getJSON('//hamwan.k7nvh.com/network_status.json.php', function(data) {
        for (var siteid in data.SITES) {
            var site = data.SITES[siteid];
            for (var attr in site) {
                sites[siteid][attr] = site[attr];
            }
            sites[siteid].position = new google.maps.LatLng(site.LATITUDE, site.LONGITUDE);
        }
    })
    .fail(function() {
        alert("Could not load network status data! Only the coverage map will be displayed. Internet Explorer 8 is not supported.");
    })
    .always(function() {
        // yellow dot
        var clienticon = {
            url: '//maps.gstatic.com/mapfiles/mv/imgs2.png',
            anchor: new google.maps.Point(6, 6),
            origin: new google.maps.Point(25, 104),
            size: new google.maps.Size(12, 12)
        }

        // orangered dot
        var surveyicon = {
            url: '//maps.gstatic.com/mapfiles/mv/imgs2.png',
            anchor: new google.maps.Point(4, 4),
            origin: new google.maps.Point(3, 124),
            size: new google.maps.Size(9, 9)
        }

        // Add sites to map
        for (var siteid in sites) {
            var site = sites[siteid]
            var sitemarker = new google.maps.Marker({
                position: site.position,
                icon: {
                    url: site.icon,
                    anchor: new google.maps.Point(24, 25),
                    scaledSize: new google.maps.Size(50, 50)
                },
                map: map,
                title: site.NAME,
                comment: "<h3>" + site.NAME + "</h3><p>" + site.COMMENT + "</p>"
            });

            // Add clients to map
            for (var clientid in site.CLIENTS) {
                var client = site.CLIENTS[clientid];
                client.position = new google.maps.LatLng(client.LATITUDE, client.LONGITUDE);
                var clientmarker = new google.maps.Marker({
                    position: client.position,
                    icon: surveyicon,
                    map: map,
                    title: client.NAME,
                    comment: "<h3>" + client.NAME + "</h3>" + (client.TYPE == "SURVEY" ? "<p>Signal survey</p>" : "") + "<ul><li>distance: " + distHaversine(client.position, site.position) + " miles </li><li>signal strength: " + client.STRENGTH + " dBm</li>" + (client.SPEED ? "<li>speed: " + client.SPEED/1000/1000 + " Mbps</li>" : '') + "</ul><p>" + client.COMMENT + "</p>"
                });
                google.maps.event.addListener(clientmarker, 'click', function() {
                    infowindow.setContent(this.comment);
                    infowindow.open(map, this);
                });

                // Add client links to map
                if (client.STRENGTH) {
                    var linkpolyline = new google.maps.Polyline({
                        path: [site.position, client.position],
                        strokeColor: linkColor(client),
                        strokeOpacity: linkOpacity(),
                        strokeWeight: linkWidth(client)
                    });
                    linkpolyline.setMap(map);
                }
            }

            // Add PtP links to map
            for (var linkid in site.LINKS) {
                var link = site.LINKS[linkid]
                // only plot each link once (ignore reciprocal links)
                if (siteid == link.SITE1_ID) {
                    var linkpolyline = new google.maps.Polyline({
                        path: [site.position, sites[link.SITE2_ID].position],
                        strokeColor: linkColor(link),
                        strokeOpacity: linkOpacity(),
                        strokeWeight: linkWidth(link)
                    });
                    linkpolyline.setMap(map);
                }
                // Add link data to comment of both associated sites
                sitemarker.comment += "<h3>" + link.NAME + " link</h3><ul><li>distance: " + distHaversine(sites[link.SITE1_ID].position, sites[link.SITE2_ID].position) + " miles </li><li>signal strength: " + link.STRENGTH + " dBm</li>" + "<li>speed: " + link.SPEED/1000/1000 + " Mbps</li></ul><p>" + link.COMMENT + "</p>"
            }

            // create site infowindow (now that link data is incorporated)
            google.maps.event.addListener(sitemarker, 'click', function() {
                infowindow.setContent(this.comment);
                infowindow.open(map, this);
            });

        }
    });

    // Add mesh nodes kml map
    //var ActiveNodesLayer = new google.maps.KmlLayer('http://nodes.map.nwmesh.us/');
    //ActiveNodesLayer.setMap(map);

    // Add the controls to the map
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(document.getElementById('map_search'));
}
google.maps.event.addDomListener(window, 'load', initialize);
