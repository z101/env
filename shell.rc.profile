# rc shell profile
# $home/lib/profile

PATH=$PLAN9/bin:$PATH
MANPATH=$PLAN9/share/man:/usr/share/man

ps1='; '
hname=`{hostname}
tab='	'

fn setprompt {
	if(~ `{pwd} '/')
		prompt=($hname^' /'^$ps1 $tab)
	if not {
		ifs='
' { ppt=$hname^' '^`{basename `{pwd}}^$ps1 }
		prompt=($ppt $tab)
	}
}

fn cd {
	builtin cd $1 &&
	switch($#*){
	case 0
		dir=$home
		prompt=($hname^$ps1 $tab)
	case *
		switch($1){
		case /*
			dir=$1
			setprompt
		case */* ..*
			dir=()
			setprompt
		case *
			dir=()
			setprompt
		}
	}
}
fn pwd {
	if(~ $#dir 0)
		dir=`{/bin/pwd}
	echo $dir
}
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

if (test -f $home/lib/profile.local)
	. $home/lib/profile.local

stty iutf8
tabs 4 >/dev/null >[2=1]
cd `{ pwd }
#cd
#clear
