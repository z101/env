# rc shell profile
# $home/lib/profile

PATH=$PLAN9/bin:$PATH
MANPATH=$PLAN9/share/man

fn ls { builtin ls -F $* }

tabs 4
clear