PXE Script Dispatcher
---------------------

Copy or symlink pxeboot.cgi into your webserver webroot, and make it executable
(chmod +x). Enable your web server to execute CGI scripts.

Add the following to your dhcpd.conf to allow fetching of the iPXE boot
script when running under iPXE. The file undionly.kpxe is part of the iPXE
project.

    allow booting;
    next-server 10.1.1.2;
    if exists user-class and ( option user-class = "gPXE" or option user-class = "iPXE" ) {
            filename "http://your.server.here/path/to/pxeboot.cgi";
    } else {
            filename "undionly.kpxe";
    }

The iPXE scripts should be named $root_url/pxeboot/<lowercase-mac-without-colons>.pxe.

If $root_url/pxeboot/default.pxe is found, it is run if no MAC-specific script is found.

$root_url is the url mentioned in the dhcpd.conf chunk above minus
'/pxeboot.cgi'.

If you also install pxelinux.0 in the same folder as pxeboot.cgi, it will try
to load it unless any other script was found.

This boot script generator should work with both gPXE and iPXE, but for any
kind of sophisticated scripting only iPXE has enough features.

AUTHOR
------

Robin Smidsrød <robin@smidsrod.no>

COPYRIGHT
---------

Copyright (C) Robin Smidsrød. All rights reserved.

This script is licensed under the same terms as the iPXE project itself.

SEE ALSO
--------

* [iPXE command line overview](http://www.ipxe.org/cmd)
* [iPXE project](http://www.ipxe.org/)
* [Etherboot/gPXE project page](http://www.etherboot.org/)
