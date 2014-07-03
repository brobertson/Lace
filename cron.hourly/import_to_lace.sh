#!/bin/bash
FLAG_FILE=/tmp/import_from_lace_running
if [ -e $FLAG_FILE ]
then 
  exit 0
fi
touch $FLAG_FILE
rsync -urLvzhe ssh broberts@saw.sharcnet.ca:/work/broberts/Output/Jpgs/ /mnt/Europe/Lace_Resources/Images/Color/
rsync -urLvzhe ssh broberts@saw.sharcnet.ca:/work/broberts/Output/Tars/ /mnt/Europe/Lace_Resources/Inbox/
for file in `comm -23 <(ls -a /mnt/Europe/Lace_Resources/Inbox/) <(ls -a /mnt/Europe/Lace_Resources/Outbox)`
do
python /home/brucerob/Lace/import_to_lace_from_tar.py "/mnt/Europe/Lace_Resources/Inbox/$file"
done
rm $FLAG_FILE
