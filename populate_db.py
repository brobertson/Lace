import lace
from lace import Archivetext
from lace import Ocrrun
from lace import db
import os
import sys
from lace import collect_archive_text_info
from lxml import etree
from lace import get_runs
import glob
db.create_all()
i = 0
for meta_file in os.listdir(sys.argv[1]):
    print i, meta_file
    text_info = collect_archive_text_info(os.path.join(sys.argv[1] + meta_file))
    existing_text_info_record = db.session.query(Archivetext).filter_by(archive_id=text_info['identifier']).first()
    if not existing_text_info_record:
        t = Archivetext(title = text_info['title'], creator = text_info['creator'], publisher = text_info['publisher'],
                    date = text_info['date'], archive_id = text_info['identifier'], ppi = text_info['ppi'],
                               volume = text_info['volume'])
        try:
            db.session.add(t)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
    try:
        (run_dir_base,runs) = get_runs(text_info['identifier'])
        print "rdb:", run_dir_base
        print 'runs: ', runs
    except:
        print 'no runs for', text_info['identifier']
        #raise
    if (len(runs) > 0):
        for run in runs:
            r = Ocrrun(archivetext_id = text_info['identifier'], classifier = run['classifier'], date = run['date'])
            try:
                db.session.add(r)
                db.session.commit()
                #print '\t',r
            except:
                print "rolling back"
                raise
            for output_type in ['selected_hocr_output_spellchecked','selected_hocr_output','combined_hocr_output']:
                trial_glob_file = run_dir_base + '*' + output_type
                a_hocr_dir = ''
                try:
                    a_hocr_dir = glob.glob(trial_glob_file)[0]
                    print 'a_hocr_dir', a_hocr_dir
                except:
                    print 'no data for', trial_glob_file
                if a_hocr_dir:
                    for file_name in glob.glob(a_hocr_dir + '/' + '*.html'):
                        print  'file_name:', file_name
                        try:
                            (name,page_number,filetype,thresh,thresh_value) = os.path.basename(file_name)[:-5].split('_')
                            print 'name', name
                            print 'page', page_number
                            print 'filetype', filetype
                            print 'thresh_value', thresh_value
                        except:
                            (name, page_number) = os.path.basename(file_name)[:-5].split('_')
                            print 'page', page_number
    i = i + 1
texts = Archivetext.query.all()
runs = Ocrrun.query.all()
print "run count: ", len(runs)
#for text in texts:
#    print text.archive_id

