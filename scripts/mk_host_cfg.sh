cat d|awk -F ":" '{ cmd = "echo "$4"|base64"; cmd|getline var; close(cmd); print "["$1"]\ndomain="$2"\nhost="$3"\nport="$5"\nuser="$2"\npassword="var"\nworkdir=/home/"$2}'