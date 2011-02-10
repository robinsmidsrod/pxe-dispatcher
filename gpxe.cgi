#!/usr/bin/perl

use strict;
use warnings;

use CGI ();

my $q = CGI->new();

# Build root url of script
my $root_url = $q->url( -path_info => 1 );
$root_url =~ s{/gpxe\.cgi$}{}; # Strip /gpxe.cgi

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

# Send default gPXE script that chainloads and calls script again with MAC address
sub no_params {
    print $q->header('text/plain'), <<"EOM";
#!gpxe
echo Loading gPXE script for \${net0/mac}
chain $root_url/gpxe.cgi?mac=\${net0/mac}
EOM
    return 1;
}

# Chainload $root_url/gpxe/<mac-without-colons>.gpxe
# or $root_url/pxelinux.0 (if exists)
# or just exit (if none found)
sub script_for_mac {
    my ($mac) = @_;
    my $filename = $mac;
    $filename =~ s/://g;
    $filename = "gpxe/$filename.gpxe";
    my $url = "$root_url/$filename";
    if ( -r $filename ) {
        print $q->header('text/plain'), <<"EOM";
#!gpxe
echo
echo Loading gPXE script for $mac
chain $url
EOM
        return 1;
    }
    
    # Abort boot sequence if no pxelinux.0 found
    unless ( -r 'pxelinux.0' ) {
        print $q->header('text/plain'), <<'EOM';
#!gpxe
echo
echo URL unavailable: $url
echo No PXELinux available, aborting netboot
exit
EOM
        return 1;
    }
        
    # Boot with default PXELinux
    print $q->header('text/plain'), <<"EOM";
#!gpxe
echo
echo URL unavailable: $url
echo Loading PXELinux for $mac
chain $root_url/pxelinux.0
EOM
    return 1;
}
