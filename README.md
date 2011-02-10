gPXE Script Dispatcher
----------------------

Copy or symlink gpxe.cgi into your webserver webroot, and make it executable
(chmod +x). Enable your web server to execute CGI scripts.

Add the following to your dhcpd.conf to allow fetching of the gPXE boot
script when running under gPXE. The file undionly.kpxe is part of the gPXE
project.

    allow booting;
    next-server 10.1.1.2;
    if exists user-class and option user-class = "gPXE" {
            filename "http://your.server.here/path/to/gpxe.cgi";
    } else {
            filename "undionly.kpxe";
    }

If you also install pxelinux.0 in the same folder as gpxe.cgi, it will try
to load it unless any other script was found.

The gPXE scripts should be named $root_url/gpxe/<lowercase-mac-without-colons>.gpxe.

$root_url is the url mentioned in the dhcpd.conf chunk above minus
'/gpxe.cgi'.
