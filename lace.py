from flask import Flask, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
from settings import APP_ROOT, POSSIBLE_HOCR_VIEWS,PREFERENCE_OF_HOCR_VIEWS
from local_settings import database_uri
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/6test.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://brucerob:lace@127.0.0.1:3306/lace"
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db = SQLAlchemy(app)

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
def index():
    from flask import render_template
    return render_template('basic.html', name="foo")


@app.route('/about')
def about():
    return index()


@app.route('/stats')
def stats():
    from flask import render_template
    text_count = len(Archivetext.query.all())
    page_count = len(Outputpage.query.all())
    run_count = len(Ocrrun.query.all())
    return render_template('stats.html', text_count = text_count, page_count = page_count, run_count = run_count)


def pad_page_num_for_archive(num):
    return num.zfill(4)


def url_for_page_image(text_id, page_num):
    file_address = 'Images/Color/' + text_id + \
        '_color/' + text_id + '_' + pad_page_num_for_archive(str(page_num)) + '.jpg'
    return url_for('static', filename=file_address)


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
    return side_by_side_view(html_path)


@app.route('/sidebysideview/<path:html_path>')
def side_by_side_view(html_path):
    from flask import render_template
    sp = get_sister_pages(html_path)
    number_of_sister_pages = len(sp)
    import os.path
    filename = os.path.basename(html_path)
    this_page_index = sp.index(filename)
    # TODO figure out how to use url_for here:
    html_url = '/text/' + html_path
    print "this page index: ", this_page_index
    page_before_exists = (not this_page_index == 0)
    page_after_exists = (not this_page_index == number_of_sister_pages)
    if page_before_exists:
        page_before = url_for('side_by_side_view', html_path=os.path.join(
            os.path.dirname(html_path), sp[this_page_index - 1]))
    else:
        page_before = None
    if page_after_exists:
        page_after = url_for('side_by_side_view', html_path=os.path.join(
            os.path.dirname(html_path), sp[this_page_index + 1]))
    else:
        page_after = None
    try:
        (text_id, page_num) = filename.split('_')
        page_num = page_num[0:-5]
    except ValueError:
        (long_text_id, page_num, file_type, thresh, threshvalue) = filename.split('_')
        text_id = long_text_id[7:]
    (view, date, classifier) = parse_path(html_path)
    pagination_array = make_pagination_array(
        number_of_sister_pages, this_page_index, 25, html_path, sp)
    try:
        text_info = get_text_info(text_id)
        return render_template('sidebyside.html', html_path=html_url,
                               text_id=text_id,
                               text_info=text_info,
                               image_path=
                               url_for_page_image(text_id, page_num),
                               classifier=classifier, date=date, view=view,
                               page_num_normalized=int(page_num),
                               page_after_exists=page_after_exists,
                               page_before_exists=page_before_exists,
                               page_before=page_before,
                               page_after=page_after,
                               pagination_array=pagination_array)
    except IOError:
        return render_template('no_such_text_id.html', textid=text_id), 404


def make_pagination_array(sister_outputpages, this_page, steps):
    this_index = sister_outputpages.index(this_page)
    stepsize = int(len(sister_outputpages)/ steps)
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
    print pagination_array
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


    metadata_file = open(APP_ROOT + url_for(
        'static', filename="Metadata/" + textid + '_meta.xml'))
    info = collect_archive_text_info(metadata_file)
    return info

@app.route('/runinfo', methods=['GET'])
def runinfo():
    from flask import request, render_template
    text_id = request.args.get('text_id', '')
    date = request.args.get('date', '')
    classifier = request.args.get('classifier', '')
    path_to_info = text_id + '/' + date + '_' + classifier + '_selected_hocr_output/info.txt'
    path_to_3d =  url_for('static', filename='Texts/' + text_id + '/' + date + '_' + classifier + '_selected_hocr_output/3d.png')
    path_to_chart = url_for('static', filename='Texts/' + text_id + '/' + date + '_' + classifier + '_selected_hocr_output/' + date  + '_' + classifier + '_summary.png')
    info_file = open(get_absolute_textpath(path_to_info))
    info = info_file.read()
    text_info = get_text_info(text_id)
    return render_template('run_info.html', text_id = text_id, date = date, classifier = classifier, text_info= text_info, info=info, path_to_3d = path_to_3d, path_to_chart = path_to_chart)


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
    sort_by = request.args.get('sort_by')
    works = Archivetext.query.all()
    works = [work for work in works if work.ocrruns]
    sorted_works = sorted(works, key=lambda work: work.creator)
    if sort_by == 'date':
        sorted_works = sorted(works, key=lambda work: work.date)
    if sort_by == 'run_date':
        sorted_works = sorted(works, key=get_latest_run)
    if sort_by == 'quality':
        sorted_works = sorted(works, key=get_best_b_score, reverse=True)
    work_count = len(works)
    return render_template('catalog.html', works = sorted_works, work_count = work_count)

def get_latest_run(archivetext):
    ocrruns = archivetext.ocrruns
    sorted_ocrruns = sorted(ocrruns, key=lambda ocrrun: ocrrun.date, reverse=True)
    return sorted_ocrruns[0].date

def get_best_b_score(archivetext):
    ocrruns = archivetext.ocrruns
    print "guessing at length:", len(ocrruns[0].prefered_hocrtype().outputpages)
    sorted_ocrruns = sorted(ocrruns, key=lambda ocrrun: (ocrrun.total_b_score()/float(len(ocrrun.prefered_hocrtype().outputpages)+0.001)), reverse=True)
    return (sorted_ocrruns[0].total_b_score()/float(len(sorted_ocrruns[0].prefered_hocrtype().outputpages)+0.001))
@app.route('/runs/<text_id>')
def runs(text_id):
    from flask import render_template
    text = Archivetext.query.filter_by(archive_number = text_id).first()
    print text
    return render_template('runs.html', text_info = text)


@app.route('/text/<path:textpath>')
def hello_world(textpath):
    from local_settings import textpath_root
    from lxml import etree
    a =  open(textpath_root+textpath)#a = get_absolute_textpath(textpath)
    print "app root: ", APP_ROOT
    try:
        tree = etree.parse(a)
        root = tree.getroot()
        head_element = tree.xpath("/html:html/html:head | /html/head",
                                  namespaces={
                                  'html': "http://www.w3.org/1999/xhtml"})[0]
        css_file = url_for('static', filename='hocr.css')
        style = etree.SubElement(
            head_element, "link", rel="stylesheet", type="text/css",
            href=css_file)
        return etree.tostring(root, pretty_print=True)
    except Exception as e:
        print "We're upset about:", e
        pass

#text_id, run-date, page_number, hocr_view

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
    page_after_exists = (not this_page_index == number_of_sister_pages)
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
                               html_url = url_for('hello_world',textpath = this_page.relative_path),
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
        return render_template('no_such_text_id.html', textid=text_id), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
