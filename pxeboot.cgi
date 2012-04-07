#!/usr/bin/perl

use strict;
use warnings;

use CGI ();

# Change this line if you rename the script
my $myself = "pxeboot.cgi";
my $subdir = "pxeboot";
my $ext = "pxe";

my $q = CGI->new();

# Build root url of script
my $root_url = $q->url( -path_info => 1 );
$root_url =~ s{/\Q$myself\E$}{}; # Strip out filename of this script from URL

# If mac query param is present, and looks like a mac address,
# try to load specific script, else load chaining script
my $hex = qr/[0-9a-f]{2}/;
if ( $q->param('mac') and lc( $q->param('mac') ) =~ m{\A(?:$hex:){5}$hex\Z} ) {
    script_for_mac( lc( $q->param('mac') ) );
}
else {
    no_params();
}

exit;

# Send default iPXE script that chainloads and calls script again with MAC address
sub no_params {
    print $q->header('text/plain'), <<"EOM";
#!gpxe
echo Loading PXE script for \${mac}
chain $root_url/$myself?uuid=\${uuid}&mac=\${mac}&busid=\${busid}&ip=\${ip}&hostname=\${hostname:uristring}&serial=\${serial:uristring}&asset=\${asset:uristring}&manufacturer=\${manufacturer:uristring}&product=\${product:uristring}
EOM
    return 1;
}

# Chainload $root_url/$subdir/<mac-without-colons>.$ext
# or $root_url/pxelinux.0 (if exists)
# or just exit (if none found)
sub script_for_mac {
    my ($mac) = @_;
    my $filename = $mac;
    $filename =~ s/://g;
    $filename = "$subdir/$filename.$ext";
    my $url = "$root_url/$filename";
    if ( -r $filename ) {
        print $q->header('text/plain'), <<"EOM";
#!gpxe
echo
echo Loading PXE script for $mac
chain $url
EOM
        return 1;
    }

    # Boot with pxeboot/default.$ext
    if ( -r "$subdir/default.$ext" ) {
        print $q->header('text/plain'), <<"EOM";
#!gpxe
echo
echo Loading $subdir/default.$ext for $mac
chain $root_url/$subdir/default.$ext
EOM
        return 1;
    }

    # Boot with default PXELinux
    if ( -r 'pxelinux.0' ) {
        print $q->header('text/plain'), <<"EOM";
#!gpxe
echo
echo URL unavailable: $url
echo Loading PXELinux for $mac
chain $root_url/pxelinux.0
EOM
        return 1;
    }

    # Abort boot sequence if no pxelinux.0 found
    print $q->header('text/plain'), <<'EOM';
#!gpxe
echo
echo URL unavailable: $url
echo No PXELinux available, aborting netboot
exit
EOM
    return 1;
}
