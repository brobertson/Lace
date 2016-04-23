# -*- coding: UTF-8 -*-
from flask import Flask, url_for, request, abort, send_file
from flask.ext.sqlalchemy import SQLAlchemy
from settings import APP_ROOT, POSSIBLE_HOCR_VIEWS,PREFERENCE_OF_HOCR_VIEWS
from local_settings import database_uri, exist_db_uri
from flaskext.markdown import Markdown
from authentication import requires_auth
from PIL import Image
import StringIO
import urllib
app = Flask(__name__)
Markdown(app)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db = SQLAlchemy(app)

#rank the hocr views
hocr_view_score = dict()
for index, item in enumerate(POSSIBLE_HOCR_VIEWS):
    for index2, item2 in enumerate(PREFERENCE_OF_HOCR_VIEWS):
        if item2 == item:
            hocr_view_score[index] = index2


class Archivetext(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    archive_number = db.Column(db.String(64), index = True, unique = True)
    creator = db.Column(db.String(120), index = True, unique = False)
    publisher = db.Column(db.String(120), index = True, unique = False)
    date = db.Column(db.String(120), index = True, unique = False)
    title = db.Column(db.String(120), index = True, unique = False)
    volume = db.Column(db.String(120), index = True, unique = False)
    ppi = db.Column(db.String(120), index = True, unique = False)
    ocrruns = db.relationship("Ocrrun", backref=db.backref('archivetext'))
    #ocrrun_id = db.Column(db.Integer, db.ForeignKey('ocrrun.id'))
    #ocrruns = db.relationship('Ocrrun', backref=db.backref('archivetext', lazy='dynamic'))
    def __repr__(self):
        return '<Archive_id %r>' % (self.archive_number)
    def date_sorted_runs(self):
        out = sorted(self.ocrruns, key=lambda x: x.date, reverse=True)
        for run in out:
            print run, run.date
        return out

class Ocrrun(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    classifier = db.Column(db.String(64), index = True, unique = False)
    date = db.Column(db.String(120), index=True, unique = False)
    hocrtypes = db.relationship("Hocrtype", backref=db.backref('ocrrun'))
    archivetext_id = db.Column(db.Integer, db.ForeignKey('archivetext.id'))

    def total_b_score(self):
        int_for_combined = int_for_hocr_type_string('selected_hocr_output')
        selected_hocrtype = next(hocrtype for hocrtype in self.hocrtypes if hocrtype.hocr_type == int_for_combined)
        return selected_hocrtype.total_b_score()
    def prefered_hocrtype(self):
        for hocr_type in PREFERENCE_OF_HOCR_VIEWS:
            current_type = int_for_hocr_type_string(hocr_type)
            for hocrtype in self.hocrtypes:
                if hocrtype.hocr_type == current_type:
                    return hocrtype
        raise ValueError
    def sorted_hocrtypes(self):
        return sorted(self.hocrtypes)
    def link_to_tar_file(self):
	import os.path
	filename='Tars/robertson_' + self.date + '_' + self.archivetext.archive_number + '_jp2_' + self.classifier + '_full.tar.gz'
	if os.path.isfile(APP_ROOT + '/static/' + filename):
		print "yep, ", filename, "is a file"
        	return url_for('static', filename=filename)
	else:
		filename = 'Tars/robertson_' + self.date + '_' + self.archivetext.archive_number + '_' + self.classifier + '_full.tar.gz'
		if os.path.isfile(APP_ROOT + '/static/' + filename):
                	print "yep, ", filename, "is a file"
                	return url_for('static', filename=filename)
		else:
			return None
    def link_to_zip_file(self):
	import os.path
        filename='Zips/robertson_' + self.date + '_' + self.archivetext.archive_number + '_jp2_' + self.classifier + '_full.zip'
        if os.path.isfile(APP_ROOT + '/static/' + filename):
                print "yep, ", filename, "is a file"
                return url_for('static', filename=filename)
        else:
                filename = 'Zips/robertson_' + self.date + '_' + self.archivetext.archive_number + '_' + self.classifier + '_full.zip'
                if os.path.isfile(APP_ROOT + '/static/' + filename):
                        print "yep, ", filename, "is a file"
                        return url_for('static', filename=filename)
                else:
                        return None
    def archive_anchors(self):
	zip_anchor = ""
	tar_anchor = ""
	zip_link = self.link_to_zip_file()
	if zip_link:
		zip_anchor = '<a href="' + zip_link + '">.zip</a>'
	tar_link = self.link_to_tar_file()
	if tar_link:
		tar_anchor = '<a href="' + tar_link + '">.tar.gz</a>'
	return tar_anchor + '&nbsp;' + zip_anchor

    def __repr__(self):
         return '<Ocrrun %r>' % (str(self.archivetext_id) + ' ' + self.date)

class Hocrtype(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    ocrrun_id = db.Column(db.Integer, db.ForeignKey('ocrrun.id'))
    hocr_type = db.Column(db.Integer, index = True, unique = False)
    outputpages = db.relationship("Outputpage", backref=db.backref('hocrtype'))
    def hocr_type_string(self):
        return POSSIBLE_HOCR_VIEWS[self.hocr_type]
    def total_b_score(self):
        total = 0.0
        for outputpage in self.outputpages:
            total = total+ outputpage.b_score
        if total < 0:
            total = 0.0
        return total
    def __gt__(self, other):
        return hocr_view_score[self.hocr_type] > hocr_view_score[other.hocr_type]
    def __lt__(self, other):
        return not hocr_view_score[self.hocr_type] > hocr_view_score[other.hocr_type]

def int_for_hocr_type_string(hocr_type):
    return POSSIBLE_HOCR_VIEWS.index(hocr_type)


def string_for_hocr_type_int(hocr_int):
    return POSSIBLE_HOCR_VIEWS[hocr_int]


class Outputpage(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    b_score  =  db.Column(db.Float, index = True, unique = False)
    page_number = db.Column(db.Integer, index = True, unique = False)
    threshold = db.Column(db.Integer, index = True, unique = False)
    hocrtype_id = db.Column(db.Integer, db.ForeignKey('hocrtype.id'))
    relative_path = db.Column(db.String(200), index = False, unique = True)


    def __repr__(self):
        return '<Outputpage ' + str(self.id) + ">"


@app.route('/')
@requires_auth
def index():
    from flask import render_template
    return render_template('index.html')


@app.route('/about')
def about():
    from flask import render_template
    return render_template('about.html')

@app.route('/stats')
def stats():
    from flask import render_template
    text_count = Archivetext.query.count()
    page_count = Outputpage.query.count()
    combined_hocr_types = Hocrtype.query.filter(Hocrtype.hocr_type == int_for_hocr_type_string('combined_hocr_output')).all()
    total = 0
    for cht in combined_hocr_types:
        total = total + len(cht.outputpages)
    run_count = Ocrrun.query.count()
    return render_template('stats.html', text_count = text_count, page_count = page_count, run_count = run_count, unique_page_count = total)


@app.route('/search', methods=['GET'])
def search():
    classifier = request.args.get('classifier', '')
    archive_id = request.args.get('id','')
    print "querying classifier: ", classifier
    from flask import render_template
    runs = Ocrrun.query.filter_by(classifier = classifier).all()
    print runs
    sorted_runs = sorted(runs, key=lambda run: run.date)
    print sorted_runs
    return render_template('search.html', runs = runs, classifier=classifier)


@app.route('/nextsteps')
def nextsteps():
    from flask import render_template
    return render_template('nextsteps.html')

@app.route('/faq')
def faq():
    from flask import render_template
    return render_template('faq.html')

@app.route('/guide')
def guide():
    from flask import render_template
    return render_template('guide.html')

@app.route('/datech14')
def datech():
    from flask import render_template
    return render_template('datech2014.html')

@app.route('/gallery')
def gallery():
    from flask import render_template
    return render_template('gallery.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    import html2text
    from lxml import html
    this_page = Outputpage.query.filter_by(id = 8310578).first()
    the_html = view_html(this_page.relative_path)
    return html2text.html2text(the_html)
    #from flask import render_template
    #return render_template('index.html')


@app.route('/classifiers')
def classifiers():
    from flask import render_template
    classifiers = db.session.query(Ocrrun.classifier).distinct()
    print classifiers
    return render_template('classifiers.html', classifiers = classifiers)


def pad_page_num_for_archive(num):
    return num.zfill(4)


def url_for_page_image(text_id, page_num):
    file_address = 'Images/Color/' + text_id + \
        '_color/' + text_id + '_' + pad_page_num_for_archive(str(page_num)) + '.jpg'
    return url_for('static', filename=file_address)

def bbox_to_array(bbox_string):
    fudge = 20 
    elements = bbox_string.split(' ')
    elements = elements[1:]
    elements = [int(x) for x in elements]
    elements = [elements[0] - fudge, elements[1] - fudge, elements[2], elements[3]  ]
    return elements

def image_region_from_bbox_string(image, bbox_string):
    image_scale = 0.3
    values = bbox_to_array(bbox_string)
    values = [int(image_scale*x) for x in values]
    region = image.crop(values)
    return region

def serve_pil_image(pil_img):
    img_io = StringIO.StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def encode_pil_image(pil_img):
       img_io = StringIO.StringIO()
       pil_img.save(img_io, 'JPEG', quality=70)
       img_io.seek(0)
       return img_io.getvalue().encode("base64")

def url_for_run_details(endpoint, run_details):
    return url_for(endpoint, text_id=run_details['text_id'],
                   page_num=run_details['page_num'],
                   classifier=run_details['classifier'],
                   date=run_details['date'], view=run_details['view'])


@app.route('/query', methods=['GET'])
def query():
    from flask import request
    run_details = {}
    run_details['text_id'] = request.args.get('text_id', '')
    run_details['page_num'] = request.args.get('page_num', '')
    run_details['classifier'] = request.args.get('classifier', '')
    run_details['date'] = request.args.get('date', '')
    run_details['view'] = request.args.get('view', '')
    html_path = textpath_for_run_details(run_details)
    return side_by_side_view2(html_path)

def make_pagination_array(sister_outputpages, this_page, steps):
    this_index = sister_outputpages.index(this_page)
    print "this_index", this_index
    stepsize = int(len(sister_outputpages)/ steps)
    if stepsize == 0:
	stepsize = 1
        steps = len(sister_outputpages)
    print "stepsize:", stepsize
    my_place = (this_index / stepsize)
    pagination_array = []
    is_current = False
    for i in range(steps):
        if i == my_place:
            current_index = this_index
            is_current = True
        else:
            current_index = stepsize * i
            is_current = False
        pagination_array.append([(current_index + 1), url_for('side_by_side_view2',outputpage_id = str(sister_outputpages[current_index].id)), is_current])
    #print pagination_array
    return pagination_array


def parse_path(textpath):
    import os.path
    last_dir = os.path.basename(os.path.dirname(textpath))
    # last_dir = os.path.dirname(textpath)
    return parse_dir(last_dir)


def get_absolute_textpath(textpath):
    return APP_ROOT + '/static/Texts/' + textpath #url_for('static', filename="Texts/" + textpath)


def get_sister_pages(textpath):
    import os.path
    import os
    ab_textpath = get_absolute_textpath(textpath)
    dir_contents = os.listdir(os.path.dirname(ab_textpath))
    return sorted(dir_contents)


def textfile_exists(textpath):
    import os.path
    return os.path.isfile(get_absolute_textpath(textpath))


def textpath_for_run_details(run_details):
    return run_details['text_id'] + '/' + run_details['date'] + '_' + run_details['classifier'] + '_' + run_details['view'] + '/' + run_details['text_id'] + '_' + run_details['page_num'] + ".html"


def page_offset(run_details, offset):
    new_page_num = pad_page_num_for_archive(
        str(int(run_details['page_num']) + offset))
    run_details_copy = dict(run_details)
    run_details_copy['page_num'] = new_page_num
    print new_page_num
    return run_details_copy


def page_offset_exists(run_details, offset):
    run_details = page_offset(run_details, offset)
    return textfile_exists(textpath_for_run_details(run_details))

"""Database material here"""
@app.route('/render_page', methods=['GET'])
def render_page():
    hocrtype = Hocrtype.query.filter_by(id = int(request.args.get('hocrtype_id',''))).first()
    pages = hocrtype.outputpages
    half_way = int(len(pages) / 2)
    page = hocrtype.outputpages[half_way]#Outputpage.query.filter_by(ocrrun_id =  int(request.args.get('run_id',''))).first()
    return side_by_side_view2(page.id)

def process_page(page_path):
    from flask import render_template
    return render_template('textinfo.html', name=page_path)


@app.route('/textinfo/<archive_number>')
def get_text_info(archive_number):
    from flask import render_template
    info = Archivetext.query.filter_by(archive_number = archive_number).first()
    return render_template('textinfo.html', text_info = info)


@app.route('/catalog', methods=['GET'])
def catalog():
    from flask import render_template
    print request
    sort_by = request.args.get('sort_by')
    reverse = bool(request.args.get('reverse'))
    if not reverse:
        if sort_by == 'quality':
            reverse = True
        else:
            reverse = False
    limit_str = request.args.get('limit')
    if request.args.get('limit'):
        limit = int(request.args.get('limit'))
    else:
        limit = None
    works = catalog_base(sort_by, reverse, limit)
    work_count = len(works)
    return render_template('catalog.html', works = works, work_count = work_count)


@app.route('/latest')
def latest():
    from flask import render_template
    if request.args.get('count'):
        count = int(request.args.get('count'))
    else:
        count = 10

    works = catalog_base('run_date', True, count)
    work_count = len(works)
    dates = []
    for work in works:
        work.run_date = get_latest_run(work)
        print work.run_date
    return render_template('latest.html', works = works, work_count = work_count)


def catalog_base(sort_by, reverse, limit):
    works = Archivetext.query.all()
    works = [work for work in works if work.ocrruns]
    sorted_works = sorted(works, key=lambda work: work.creator)
    if sort_by == 'date':
        sorted_works = sorted(works, key=lambda work: work.date)
    if sort_by == 'run_date':
        sorted_works = sorted(works, key=get_latest_run, reverse=reverse)
    if sort_by == 'quality':
        sorted_works = sorted(works, key=get_best_b_score, reverse=reverse)
    if limit:
        sorted_works = sorted_works[0:limit]
    return  sorted_works

def get_latest_run(archivetext):
    ocrruns = archivetext.ocrruns
    sorted_ocrruns = sorted(ocrruns, key=lambda ocrrun: ocrrun.date, reverse=True)
    return sorted_ocrruns[0].date


def get_best_b_score(archivetext):
    ocrruns = archivetext.ocrruns
    length = len(ocrruns[0].prefered_hocrtype().outputpages)
    print "guessing at length:", length
    sorted_ocrruns = sorted(ocrruns, key=lambda ocrrun: (ocrrun.total_b_score()/float(length+0.001)), reverse=True)
    return (sorted_ocrruns[0].total_b_score()/float(length+0.001))


@app.route('/runs/<text_id>')
def runs(text_id):
    from flask import render_template
    text = Archivetext.query.filter_by(archive_number = text_id).first()
    print text
    return render_template('runs.html', text_info = text)

@app.route('/image_test', methods=['GET'])
def serve_img():
    from flask import render_template
    bbox = request.args.get('bbox')
    file_name = request.args.get('file')
    image_file = file_name.split('.')[0] + '.jpg'
    book = request.args.get('book')
    book = book.split('/')[-1]
    img = Image.open(APP_ROOT + '/static/Images/Color/' + book + '_color/' + image_file)
    #img = Image.open('/mnt/Europe/Lace_Resources/Images/Color/490021999brucerob_color/490021999brucerob_0100.jpg')
    image_region = image_region_from_bbox_string(img, bbox)
    #return render_template("test.html", img_data=urllib.quote(encode_pil_image(image_region).rstrip('\n')))
    return serve_pil_image(image_region)

def add_css(etree,head_element, a_filename):
    if a_filename[0:5] == 'http:':
         css_file = a_filename
    else:
        css_file = url_for('static', filename=a_filename)
    style = etree.SubElement(
            head_element, "link", rel="stylesheet", type="text/css",
            href=css_file)
    return etree

def add_html_csses(etree,head_element):
    for css_file in ['hocr.css','spellcheck_report.css','tipsy.css','http://code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css']:
        add_css(etree, head_element, css_file)
    return etree

def add_javascript(etree, head_element, a_script):
    if a_script[0:5] == 'http:':
         javascript_file = a_script
    else:
        javascript_file = url_for('static', filename=a_script)
    javascript_link = etree.SubElement(
            head_element, "script", type="text/javascript",
            src=javascript_file)
    return etree

def add_html_javascripts(etree, head_element):
    #for js_file in ["javascripts/jquery.focus.js", "http://code.jquery.com/jquery-1.10.2.js", "http://code.jquery.com/ui/1.11.4/jquery-ui.js", 'javascripts/jquery.tipsy.js','javascripts/tipsy.hocr.js', 'javascripts/cts_input.js']:
    for js_file in ["http://code.jquery.com/jquery-1.10.2.js", "http://code.jquery.com/ui/1.11.4/jquery-ui.js", 'javascripts/jquery.tipsy.js','javascripts/lace_config.js', 'javascripts/tipsy.hocr.js', 'javascripts/cts_input.js']:
       add_javascript(etree, head_element, js_file)
    return etree


def get_xmldb(textpath):
    from lxml import etree
    query_base = exist_db_uri + "apps/laceApp/getFile.xq?filePath="
    #cut the 'static/Texts/' from the front of the textpath
    textpath = textpath[13:]
    print "altered textpath is", textpath
    tree = etree.parse(query_base + textpath)
    return tree

#def add_editable_tags(etree, head_element):
#     dl_button = etree.SubElement(
#     [ b.tag for b in root.iterfind(".//span") ]

@app.route('/text/<path:textpath>')

def view_html(textpath):
    from lxml import etree
    import unicodedata
    from flask import Response
    is_from_xmldb = False
    try:
        tree = get_xmldb(textpath)
        is_from_xmldb = True
    except Exception as e:
        print e
        try:
            print "hello, xmldb failed. textpath is", textpath
            a =  open(APP_ROOT+ '/' + textpath)
            tree = etree.parse(a)
        except Exception as e:
            print e
    try:
        head_element = tree.xpath("/html:html/html:head | /html/head",
                                  namespaces={
                                  'html': "http://www.w3.org/1999/xhtml"})[0]
        #css_file = url_for('static', filename='hocr.css')
        #style = etree.SubElement(
        #    head_element, "link", rel="stylesheet", type="text/css",
        #    href=css_file)
        etree = add_html_csses(etree,head_element)
        if is_from_xmldb:
            etree = add_css(etree,head_element,"is_xmldb.css")
        etree = add_html_javascripts(etree,head_element)
        #etree = add_editable_tags(etree,head_element)
        ocr_word_span_elements = tree.xpath("//html:span[@class='ocr_word'] | //span[@class='ocr_word']", namespaces={'html': "http://www.w3.org/1999/xhtml"})
        #Add onclick element so that clicking on the iframe's html will send the entire framing document
        #forward to the next page
        body = tree.xpath("//html:body | //body", namespaces={'html': "http://www.w3.org/1999/xhtml"})
        #body[0].set('onclick','return parent.page_forward()')
        page = tree.xpath("//html:div[@class='ocr_page'] | div[@class='ocr_page']", namespaces={'html': "http://www.w3.org/1999/xhtml"})
        page[0].set("title",textpath[13:]);
        #Add html buttons for editing and downloading 
        button1 = etree.SubElement(body[0], "a", download="get_filename()")
        button1.text="Download"
        button1.set("id","download")
        button1.set("onclick",'$(this).attr(\'href\', \'data:text/attachement;charset=utf-8,%EF%BB%BF\' + $(\'html\').clone().find(\'#download\').remove().end()[0].outerHTML);');
	button1.set("style","display: none;");
	for span in ocr_word_span_elements:
            span.set("contenteditable","true");
        print "file ", textpath, " has doctype ", tree.docinfo.doctype
        output =  etree.tostring(tree, pretty_print=True,encoding=unicode,doctype='<!DOCTYPE html>')# PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
        return Response(unicodedata.normalize("NFC",output), mimetype='application/xhtml+xml')
    except Exception as e:
	print e
        from flask import render_template
        return render_template('nohtmlfile.html')
	#print "We're upset about:", e
        #flask.abort() 

def html_body_elements(textpath):
    from lxml import etree
    html = view_html(textpath)
    tree = etree.parse(html)
    root = tree.getroot()
    #body_element = tree.xpath("/html:html/html:body | /html/body", namespaces={'html': "http://www.w3.org/1999/xhtml"})
    body_string = etree.tostring(root, pretty_print=True, encoding=unicode)
    #print body_string
    return unicodedata.normalize("NFC",body_string)



@app.route('/sidebysideview2/<outputpage_id>')
def side_by_side_view2(outputpage_id):
    from flask import render_template
    this_page = Outputpage.query.filter_by(id = outputpage_id).first()
    text_id = this_page.hocrtype.ocrrun.archivetext.archive_number
    page_num = this_page.page_number
    sister_outputpages = this_page.hocrtype.outputpages
    number_of_sister_pages = len(sister_outputpages)
    sorted_sister_outputpages = sorted(sister_outputpages, key=lambda outputpage: outputpage.threshold)
    sorted_sister_outputpages = sorted(sorted_sister_outputpages, key=lambda outputpage: outputpage.page_number)
    this_page_index = sorted_sister_outputpages.index(this_page)
    page_before_exists = (not this_page_index == 0)
    page_after_exists = (not this_page_index == (number_of_sister_pages - 1))
    if page_before_exists:
        page_before_id = sorted_sister_outputpages[this_page_index -1].id
        page_before = url_for('side_by_side_view2',outputpage_id = str(page_before_id))
    else:
        page_before = None
    if page_after_exists:
        page_after_id = sorted_sister_outputpages[this_page_index + 1].id
        page_after = url_for('side_by_side_view2',outputpage_id = str(page_after_id))
    else:
        page_after = None
    pagination_array = make_pagination_array(sorted_sister_outputpages,this_page,25)
    try:
        return render_template('sidebyside.html',
                               this_page = this_page,
                               html_url = url_for('view_html',textpath = this_page.relative_path),
                               #html_content = html_body_elements(this_page.relative_path),
                               text_id=text_id,
                               text_info=this_page.hocrtype.ocrrun.archivetext,
                               image_path=
                               url_for_page_image(text_id, page_num),
                               page_num_normalized=int(page_num),
                               page_after_exists=page_after_exists,
                               page_before_exists=page_before_exists,
                               page_before=page_before,
                               page_after=page_after,
                               pagination_array=pagination_array)
    except IOError:
        pass#return render_template('no_such_text_id.html', textid=text_id), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
