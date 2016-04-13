The zip file in this directory is a full backup of the eXist-db database that 
corresponds to the current state of the Lace viewing and editing service. Note 
that installing eXist-db is only necessary for editing texts.

You should 'restore' this into a eXist 2.2+ database using the instructions at 
http://exist-db.org/exist/apps/doc/backup.xml 

Doing a 'restore' will overwrite any files by the same time in your already-running
eXist-db server, possibly including your user data. 

**** It is probably only safe to do this on a fresh install. ****
