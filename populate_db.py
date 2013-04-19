import lace
from lace import Archivetext
from lace import Ocrrun
from lace import Outputpage
from lace import db
from lace import get_absolute_textpath
from lace import POSSIBLE_HOCR_VIEWS
import os
import sys
from lxml import etree
import glob
db.create_all()
i = 0
DEBUG =True
page_count = 0


def possible_output_dirs(prefix):
    import os
    import glob
    output = []
    for view in POSSIBLE_HOCR_VIEWS:
        try:
            one_dir = glob.glob(prefix + '*' + view)[0]
            output.append(one_dir)
        except:
            pass
    return output


def parse_dir(textdir):
    for view in POSSIBLE_HOCR_VIEWS:
        (before, sep, after) = textdir.partition('_' + view)
        print
        print before, sep, after
        if sep:
            parts = before.split('_')
            date = parts[0]
            classifier = '_'.join(parts[1:])
            return (view, date, classifier)
    raise ValueError(
        "Path " + textdir + " cannot be parsed with given views.")


def collect_archive_text_info(archive_xml_file):
    from lxml import etree
    # returns dictionary with appropriate single-value strings
    info = {}
    categories = ['creator', 'title', 'ppi',
                  'publisher', 'date', 'identifier', 'volume']
    tree = etree.parse(archive_xml_file)
    for category in categories:
        data = tree.xpath('/metadata/' + category + '/text()')
        try:
            info[category] = data[0]
            if len(data) > 1:
                info[category] = info[category] + ' et al.'
        except IndexError:
            info[category] =''
    return info


def get_runs(text_id):
    import os
    import glob
    path_to_runs = get_absolute_textpath(text_id)
    run_dirs = os.listdir(path_to_runs)
    run_dirs = [elem for elem in run_dirs if 'output' in elem ]
    run_dates = sorted(set([elem[0:16] for elem in run_dirs]))# gets uniq dates
    #print run_dates
    run_info = []
    for run_date in run_dates:
        run = {}
        run_details = {}
        run['date'] = run_date
        dir_for_glob =  path_to_runs + '/' + run_date
        sel_hocr_dir_glob = dir_for_glob + '*selected_hocr_output'
        sel_hocr_dir = glob.glob(sel_hocr_dir_glob)[0]
        try:
            score_file = open(sel_hocr_dir + '/best_scores_sum.txt')
            run['score'] = score_file.read()
        except IOError:
            run['score'] = 0
        (a,b,classifier) = parse_dir(sel_hocr_dir)
        run['classifier'] = classifier
        output_dirs = possible_output_dirs(dir_for_glob)
        sel_hocr_dir_output = glob.glob(sel_hocr_dir + '/*html')
        #but this is a filesystem directory, not a URL. We need to remove the path to 'static'
        #first_output = first_output[len(APP_ROOT + '/static/Texts/'):]
        run['link'] = ''#url_for('side_by_side_view', html_path = first_output)
        if len(sel_hocr_dir_output) > 0:
            run_info.append(run)
        else:
            print "there's nothing in", sel_hocr_dir
        #print run_info
    sorted_run_info = sorted(run_info, reverse=True, key=lambda run: float(run['score']))
    return (path_to_runs + '/', sorted_run_info)


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
            #db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
    else:
        print "There is already a record for", text_info['identifier'], ". Therefore not loading this..."
    (run_dir_base,runs) = get_runs(text_info['identifier'])
    try:
        (run_dir_base,runs) = get_runs(text_info['identifier'])
        if DEBUG:
            print "rdb:", run_dir_base
            print 'runs: ', runs
    except:
        print 'no runs for', text_info['identifier']
        runs = None#raise
    if (runs):
        for run in runs:
            r = db.session.query(Ocrrun).filter_by(archivetext_id = text_info['identifier']).filter_by(date=run['date']).first()
            if not r:
                r = Ocrrun(archivetext_id = text_info['identifier'], classifier = run['classifier'], date = run['date'])
                try:
                    db.session.add(r)
                    db.session.commit()
                    #print '\t',r
                except:
                    raise
            else:
                print "there is already a run for", text_info['identifier'], "on", run['date'], "with classifier", run['classifier'], ". Therefore not loading into db"
            for output_type in ['selected_hocr_output_spellchecked','selected_hocr_output','combined_hocr_output']:
                trial_glob_file = run_dir_base + run['date'] + '*_' + output_type
                print 'trial_glob_file', trial_glob_file
                a_hocr_dir = ''
                try:
                    a_hocr_dir = glob.glob(trial_glob_file)[0]
                    if DEBUG:
                        print 'a_hocr_dir', a_hocr_dir
                except:
                    print 'no data for', trial_glob_file
                if a_hocr_dir:
                    hocr_files = glob.glob(a_hocr_dir + '/' + '*.html')
                    hocr_files.sort()
                    for file_name in hocr_files:
                        acceptable_file = True
                        if DEBUG:
                            print  'file_name:', file_name
                        try:
                            (name,page_number,filetype,thresh,thresh_value) = os.path.basename(file_name)[:-5].split('_')
                            if DEBUG:
                                print 'name', name
                                print 'page', page_number
                                print 'filetype', filetype
                                print 'thresh_value', thresh_value
                                print 'output type', output_type
                        except ValueError:
                            try:
                                (name, page_number) = os.path.basename(file_name)[:-5].split('_')
                                if DEBUG:
                                    print 'page', page_number
                                    print 'output type', output_type
                            except ValueError:
                                print "can't parse filename:", file_name, "skipping this file..."
                                acceptable_file = False
                        if acceptable_file:
                            try:
                                import codecs
                                content = codecs.open(file_name, encoding="utf-8").read()
                            except:
                                print "can't read file:", file_name, "skipping this file..."
                                acceptable_file = False
                        if acceptable_file:
                            existing_page = db.session.query(Outputpage).filter_by(ocrrun_id = r.id).filter_by(output_type = output_type).filter_by(page_number = page_number).first()
                            if not existing_page:
                                p =  Outputpage(relative_path = file_name, page_number = page_number, output_type = output_type, ocrrun_id = r.id, threshold = 0)
                                try:
                                    db.session.add(p)
                                    page_count = page_count + 1#db.session.commit()
                                except:
                                    raise
    db.session.commit()
    i = i + 1
texts = Archivetext.query.all()

runs = Ocrrun.query.all()
print "run count: ", len(runs)
print "my page count: ", page_count

pages = Outputpage.query.all()
print "their page count: ", len(pages)
#for text in texts:
#    print text.archive_id

