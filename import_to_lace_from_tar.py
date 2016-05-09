# -*- coding: UTF-8 -*-
#!/usr/bin/python
from lace import  db, Archivetext, Ocrrun, Outputpage, Hocrtype, POSSIBLE_HOCR_VIEWS
import glob, os, sys, shutil, tarfile, tempfile
from lace import get_absolute_textpath, get_image_dir_path, APP_ROOT
from populate_db import get_page_scores, collect_archive_text_info, get_runs, int_for_hocr_type_string, string_for_hocr_type_int
DEBUG = True

def install_images(text_identifier):
    import urllib2
    import StringIO
    import gzip
    import tarfile
    import os
    image_tar_directory_url = "http://heml.mta.ca/LaceImages/"
    image_tar_url = image_tar_directory_url + text_identifier + "_color.tar.gz"
    temp_dir = tempfile.mkdtemp()
    tar_file_name = os.path.join(temp_dir,os.path.basename(image_tar_url))
    try:
        f = urllib2.urlopen(image_tar_url)
        print "downloading matching images. This can take minutes"
        # Open our local file for writing
        with open(tar_file_name, "wb") as tar_file_handle:
            while True:
                data = f.read(4096)
                if data:
                    tar_file_handle.write(data)
                    print ".",
                else:
                    break
    #
    # Set the file's current position to the beginning
    # of the file so that gzip.GzipFile can read
    # its contents from the top.
    #
    except Exception as e:
        print e
    print "done downloading. Extracting ..."
    try:
        tar = tarfile.open(name=tar_file_name, mode='r:gz')
    except Exception as e:
        print('ERROR file %s not a valid tar.gz file.' % image_tar_url)
        print e
    try:
        tar.extractall(path=get_image_dir_path())
    except Exception as e:
        print('ERROR couldn\'t put images in %s.' % get_image_dir_path())
        print e
textpath = get_absolute_textpath('')
db.create_all()
page_count = 0
if len(sys.argv) < 2:
    sys.exit('Usage: %s tar-gzip-file' % sys.argv[0])
for file_in in sys.argv[1:]:
    if not os.path.isfile(file_in):
        sys.exit('ERROR: tar file %s was not found!' % file_in)
    try:
        tar = tarfile.open(name=file_in,mode='r:gz')
    except:
        print('ERROR file %s not a valid tar.gz file.' % file_in)
        continue
    (route, file_name) = os.path.split(file_in)
    print file_name
    #(name_label, date, identifier, file_type, classifier,stuff)
    values = file_name.split('_')
    identifier = values[2]
    print "identifier", identifier
    id_directory = os.path.join(textpath,identifier)
    if not os.path.exists(id_directory):
        os.makedirs(id_directory)
    temp_dir = tempfile.mkdtemp()
    try:
        tar.extractall(path=temp_dir)
	#check if the tar uses the new, wrapped form
	if os.path.isdir(os.path.join(temp_dir, identifier)):
            src_dir = os.path.join(temp_dir, identifier)
	else:
	    src_dir = temp_dir
	source = os.listdir(src_dir)
        print "source: ", source
	for a_dir in source:
                print "one dir: ", a_dir
                full_path_to_a_dir = os.path.join(src_dir,a_dir)
                print "full path: ", full_path_to_a_dir
		try:
                    shutil.move(full_path_to_a_dir, id_directory)
                except:
                    print full_path_to_a_dir + " already exists."
    finally:
	shutil.rmtree(temp_dir)
    try:
        info =  collect_archive_text_info( id_directory + '/' + identifier + '_meta.xml')
        print info
    except Exception as e:
        print e
        try:
            info = collect_archive_text_info('http://www.archive.org/download/' + identifier+ '/' + identifier + '_meta.xml')
            print info
        except Exception as e:
            print e
            print('ERROR archive identifier %s is not addressable' % identifier)
            continue
    t = db.session.query(Archivetext).filter_by(archive_number=info['identifier']).first()
    if not t:
        t = Archivetext(title = info['title'], creator = info['creator'], publisher = info['publisher'],
                    date = info['date'], archive_number = info['identifier'], ppi = info['ppi'],
                               volume = info['volume'])
        try:
            db.session.add(t)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
    else:
        print "There is already a record for", info['identifier'], ". Therefore not loading this..."
    date = values[1]
    print "date", date
    try:
        (run_dir_base,runs) = get_runs(info['identifier'])
        if DEBUG:
            print "rdb:", run_dir_base
            print 'runs: ', runs
    except Exception as e:
        print e
        print('no runs for "%s"' % info['identifier'])
        print 'are you sure', file_in, 'is a archive tar file?'
        runs = None#raise
    this_date_runs = [run for run in runs if run['date'] == date]
    if len(this_date_runs) < 1:
        print 'There are no runs for date', date, 'corresponding to archive file', file_name, '... skipping'
        continue
    for run in runs:
        try:
		page_scores = get_page_scores(run_dir_base,run)
	except:
		page_scores = {} 
        r = db.session.query(Ocrrun).filter_by(archivetext_id = t.id).filter_by(date=run['date']).first()
        if not r:
            r = Ocrrun(archivetext_id = t.id, classifier = run['classifier'], date = run['date'])
            try:
                db.session.add(r)
                db.session.commit()
            except:
                raise
        else:
            print "there is already a run for", info['identifier'], "on", run['date'], "with classifier", run['classifier'], ". Therefore not loading into db"
        for output_type in POSSIBLE_HOCR_VIEWS:
            trial_glob_file = run_dir_base + run['date'] + '*_' + output_type
            if DEBUG: print 'trial_glob_file', trial_glob_file
            a_hocr_dir = ''
            try:
                a_hocr_dir = glob.glob(trial_glob_file)[0]
                if DEBUG:
                    print 'a_hocr_dir', a_hocr_dir
            except:
                print 'no data for', trial_glob_file
            if a_hocr_dir:
                type_int = int_for_hocr_type_string(output_type)
                h = db.session.query(Hocrtype).filter_by(hocr_type = type_int).filter_by(ocrrun_id = r.id).first()
                if not h:
                    h = Hocrtype(hocr_type = type_int, ocrrun_id = r.id)
                    try:
                        db.session.add(h)
                        db.session.commit()
                    except:
                        raise
                hocr_files = glob.glob(a_hocr_dir + '/' + '*.html')
                hocr_files.sort()
                for hocr_file in hocr_files:
                    acceptable_file = True
                    if DEBUG:
                        print  'hocr_file:', hocr_file
                    try:
                        (name,page_number,filetype,thresh,thresh_value) = os.path.basename(hocr_file)[:-5].split('_')
                        if DEBUG:
                            print 'name', name
                            print 'page', page_number
                            print 'filetype', filetype
                            print 'thresh_value', thresh_value
                            print 'output type', output_type
                    except ValueError:
                        try:
                            (name, page_number) = os.path.basename(hocr_file)[:-5].split('_')
                            thresh_value= 0
                            if DEBUG:
                                print 'page', page_number
                                print 'output type', output_type
                        except ValueError:
                            print "can't parse filename:", hocr_file, "skipping this file..."
                            acceptable_file = False
                    if acceptable_file:
                        existing_page = db.session.query(Outputpage).filter_by(hocrtype_id = h.id).filter_by(page_number = page_number).first()
                        if not existing_page:
                            relative_path = hocr_file.replace(APP_ROOT + '/','')
                            try:
                                page_score=page_scores[relative_path.split('/')[-1]]
                            except KeyError:
                                page_score='-1.0'
                            p =  Outputpage(relative_path = relative_path, page_number = page_number, hocrtype_id = h.id, threshold = thresh_value,b_score= page_score)
                            try:
                                db.session.add(p)
                                page_count = page_count + 1#db.session.commit()
                            except:
                                raise
        db.session.commit()
    out_dir = os.path.abspath(os.path.join(os.path.dirname(file_in), '..', 'Outbox'))
    print "out dir is:", out_dir
    try:
	#this fails on windows /vagrant
        if os.path.exists(out_dir):
            print "it exists, so we are moving", file_in, "to it"
            file_out = os.path.join(out_dir,os.path.basename(file_in))
            os.rename(file_in, file_out)
        else:
            os.rename(file_in, file_in + '-processed')
    install_images(identifier)
    



