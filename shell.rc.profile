# rc shell profile
# $home/lib/profile

PATH=$PLAN9/bin:$PATH
MANPATH=$PLAN9/share/man

fn ls { builtin ls -F $* }
fn zg { /bin/grep -ir $1 $2 }
fn zp {
	maxpnum='99'
	while(! ~ $1 ''){
		switch($1){
		case [0-9] [1-9][0-9]
			maxpnum=$1
		}
		shift
	}
	echo param: max patch num '=' $maxpnum
	patches=`{eval ls -p | sort | grep 'patch\.[0-9][0-9]\.*' | head -$maxpnum}
	for(f in $patches){
		echo ' -' applying $f...
		if(! patch -p1 < $f){
			echo [ERROR] patch "$f" failed
			exit 1
		}
	}
}

tabs 4
clear
