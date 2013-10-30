#!/usr/bin/python
from lace import  db, Archivetext, Ocrrun, Outputpage, Hocrtype, POSSIBLE_HOCR_VIEWS
import glob, os, sys, tarfile
from lace import get_absolute_textpath, APP_ROOT
from populate_db import get_page_scores, collect_archive_text_info, get_runs, int_for_hocr_type_string, string_for_hocr_type_int
DEBUG = True
textpath = get_absolute_textpath('')
db.create_all()
page_count = 0
if len(sys.argv) < 2:
    sys.exit('Usage: %s archive_id' % sys.argv[0])
t = db.session.query(Archivetext).filter_by(archive_number=sys.argv[1]).first()
print t
if not t:
    print "there is no archive id " + sys.argv[1] + " in lace"
else:
    db.session.delete(t)
    print "deleting",t
    runs = db.session.query(Ocrrun).filter_by(archivetext_id = t.id)
    for run in runs:
        print "deleting", run
        print run
        db.session.delete(run)
        hocr_types = db.session.query(Hocrtype).filter_by(ocrrun_id = run.id)
        for hocr_type in hocr_types:
            print "deleting",hocr_type
            db.session.delete(hocr_type)
            pages = db.session.query(Outputpage).filter_by(hocrtype_id = hocr_type.id)
            print "and", pages.count(), "pages"
            for page in pages:
                print "deleting page", page
                db.session.delete(page)
db.session.commit()



