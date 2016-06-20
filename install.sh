# to be run as root, possibly via sudo

#### copy files to /usr/local/bin/
cp video2gallery.py /usr/local/bin/video2gallery
cp video2trailer.py /usr/local/bin/video2trailer
cp video2webm.py /usr/local/bin/video2webm
cp video2filmstrip.sh /usr/local/bin/video2filmstrip
cp video2trailer-batch.sh /usr/local/bin/video2trailer-batch
cp video2trailer-tui.py /usr/local/bin/video2trailer-tui
cp video2trailer-compress.sh /usr/local/bin/video2trailer-compress

#### create some symblic links to shorten the command name
#unlink /usr/local/bin/v2t-compress
#ln -s /usr/local/bin/video2trailer-compress /usr/local/bin/v2t-compress
unlink /usr/local/bin/v2t
ln -s /usr/local/bin/video2trailer-tui /usr/local/bin/v2t

#### make them executable
chown root. /usr/local/bin/video2*
chmod 755 /usr/local/bin/video2*
