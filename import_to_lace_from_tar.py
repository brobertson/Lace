from lace import  db, Archivetext, Ocrrun, Outputpage, Hocrtype, POSSIBLE_HOCR_VIEWS
import os, sys, tarfile
from lace import get_absolute_textpath
from populate_db import collect_archive_text_info, get_runs
textpath = get_absolute_textpath('')
db.create_all()
if len(sys.argv) < 2:
    sys.exit('Usage: %s tar-gzip-file' % sys.argv[0])
for file_in in sys.argv[1:]:
    if not os.path.isfile(file_in):
        sys.exit('ERROR: tar file %s was not found!' % file_in)
    try:
        tar = tarfile.open(name=file_in,mode='r:gz')
    except:
        sys.exit('ERROR file %s not a valid tar.gz file.' % file_in)
    (route, file_name) = os.path.split(file_in)
    print file_name
    #(name_label, date, identifier, file_type, classifier,stuff)
    values = file_name.split('_')
    identifier = values[2]
    print "identifier", identifier
    try:
        info = collect_archive_text_info('http://www.archive.org/download/' + identifier+ '/' + identifier + '_meta.xml')
        print info
    except Exception as e:
        print e
        sys.exit('ERROR archive identifier %s is not addressable' % identifier)
    date = values[1]
    print "date", date
    id_directory = os.path.join(textpath,identifier)
    if not os.path.exists(id_directory):
        os.makedirs(id_directory)
    tar.extractall(path=id_directory)
    (run_dir_base,runs) = get_runs(info['identifier'])
    this_date_runs = [run for run in runs if run['date'] == date]
    print len(this_date_runs)




