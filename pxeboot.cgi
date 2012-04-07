#!/home/robin/perl5/perlbrew/perls/current/bin/perl

BEGIN {
    # Set to 'development' for more debug output
    $ENV{'MOJO_MODE'} = 'production';
}

use Mojolicious::Lite;

app->defaults({
    format               => 'text',
    pxe_script_extension => 'pxe',
    pxe_script_subdir    => 'pxeboot',
    script_name          => 'pxeboot.cgi', # Change this line if you rename the script
});

get '/' => sub {
    my ($self) = @_;
    # Build base url of script
    my $base_url = resolve_base_url($self);
    # If mac query param is present, and looks like a mac address,
    # try to load specific script, else load chaining script
    my $mac = resolve_mac($self->req->params);
    script_for_mac( $self, $mac ) if $mac;
    no_params($self);
};

app->start;

exit;

# Resolve base URL from HTTP request URL
sub resolve_base_url {
    my ($self) = @_;
    my $base_url = $self->req->url->clone->to_abs->query('')->fragment('');
    my $path = $base_url->path;
    my $myself = $self->stash('script_name');
    $path =~ s{/\Q$myself\E$}{}; # Strip out filename of this script from URL
    $base_url = $base_url->path($path)->to_string;
    $base_url =~ s{\?$}{}; # Get rid of question mark
    $self->app->log->debug($base_url);
    return $base_url;
}

# Resolve MAC address from HTTP request query params
sub resolve_mac {
    my ($params) = @_;
    my $hex = qr/[0-9a-f]{2}/;
    return unless $params->param('mac')
              and lc( $params->param('mac') ) =~ m{\A(?:$hex:){5}$hex\Z};
    return lc $params->param('mac');
}

# Send default iPXE script that chainloads and calls script again with MAC address
sub no_params {
    my ($self) = @_;
    my $base_url = resolve_base_url($self);
    my $myself = $self->stash('script_name');
    $self->render_text( <<"EOM" );
#!gpxe
echo Loading PXE script for \${mac}
chain $base_url/$myself?uuid=\${uuid}&mac=\${mac}&busid=\${busid}&ip=\${ip}&hostname=\${hostname:uristring}&serial=\${serial:uristring}&asset=\${asset:uristring}&manufacturer=\${manufacturer:uristring}&product=\${product:uristring}
EOM
    return 1;
}

# Chainload $base_url/$subdir/<mac-without-colons>.$ext
# or $root_url/pxelinux.0 (if exists)
# or just exit (if none found)
sub script_for_mac {
    my ( $self, $mac ) = @_;
    my $ext = $self->stash('pxe_script_extension');
    my $subdir = $self->stash('pxe_script_subdir');
    my $filename = $mac;
    $filename =~ s/://g;
    $filename = "$subdir/$filename.$ext";
    my $base_url = resolve_base_url($self);
    my $url = "$base_url/$filename";
    if ( -r $filename ) {
        $self->render_text( <<"EOM" );
#!gpxe
echo
echo Loading PXE script for $mac
chain $url
EOM
        return 1;
    }

    # Boot with pxeboot/default.$ext
    if ( -r "$subdir/default.$ext" ) {
        $self->render_text( <<"EOM" );
#!gpxe
echo
echo Loading $subdir/default.$ext for $mac
chain $base_url/$subdir/default.$ext
EOM
        return 1;
    }

    # Boot with default PXELinux
    if ( -r 'pxelinux.0' ) {
        $self->render_text( <<"EOM" );
#!gpxe
echo
echo URL unavailable: $url
echo Loading PXELinux for $mac
chain $base_url/pxelinux.0
EOM
        return 1;
    }

    # Abort boot sequence if no pxelinux.0 found
    $self->render_text( <<"EOM" );
#!gpxe
echo
echo URL unavailable: $url
echo No PXELinux available, aborting netboot
exit
EOM
    return 1;
}
