# to be run as root, possibly via sudo
cp video2gallery.py /usr/local/bin/video2gallery
cp video2trailer.py /usr/local/bin/video2trailer
cp video2webm.py /usr/local/bin/video2webm
cp video2filmstrip.sh /usr/local/bin/video2filmstrip
cp video2trailer-batch.sh /usr/local/bin/video2trailer-batch
cp video2trailer-tui.py /usr/local/bin/video2trailer-tui

unlink /usr/local/bin/v2t
ln -s /usr/local/bin/video2trailer-tui /usr/local/bin/v2t
chown root. /usr/local/bin/video2*
chmod 755 /usr/local/bin/video2*
