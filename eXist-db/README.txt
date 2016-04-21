The db/ file in this directory contains the data necessary to do editing within
Lace using an eXist-db repository. The files therein should be uploaded to
your eXist-db instance with the following command:

 sudo bin/client.sh -u [admin] -P [password] -s -c /db -p /home/laceuser/Lace/eXist-db/db

*******This is not yet a secure system. It assumes a username/password pair of laceUser/laceUser for all transactions with the database, for instance.********

