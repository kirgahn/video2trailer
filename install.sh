# to be run as root, possibly via sudo

#### copy files to /usr/local/bin/
cp v2t.py /usr/local/bin/v2t
cp v2f.sh /usr/local/bin/v2f

#### make them executable
chown root. /usr/local/bin/v2t
chmod 755 /usr/local/bin/v2t

chown root. /usr/local/bin/v2f
chmod 755 /usr/local/bin/v2f
