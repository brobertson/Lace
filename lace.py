from flask import Flask, url_for
from settings import APP_ROOT,POSSIBLE_HOCR_VIEWS
app = Flask(__name__)

@app.route('/')
def index():
    from flask import render_template
    return render_template('basic.html', name="foo")

def pad_page_num_for_archive(num):
   return num.zfill(4)

def url_for_page_image(text_id, page_num):
    file_address = 'Images/Color/'+text_id + '_color/' + text_id + '_' + page_num + '.jpg'
    return url_for('static', filename=file_address)

def url_for_run_details(endpoint, run_details):
   return url_for(endpoint, text_id = run_details['text_id'], page_num = run_details['page_num'], classifier= run_details['classifier'], date = run_details['date'], view = run_details['view'])

@app.route('/query', methods=['GET'])
def query():
   from flask import request, render_template
   run_details = {}
   run_details['text_id'] = text_id = request.args.get('text_id','')
   run_details['page_num'] = page_num = request.args.get('page_num','')
   run_details['classifier'] = classifier = request.args.get('classifier','')
   run_details['date'] = date = request.args.get('date','')
   run_details['view'] = view = request.args.get('view','')
   page_id = text_id + '_' + page_num
   html_path = textpath_for_run_details(run_details)
   return side_by_side_view(html_path)

@app.route('/sidebysideview/<path:html_path>')
def side_by_side_view(html_path): 
   from flask import render_template
   sp = get_sister_pages(html_path)
   number_of_sister_pages = len(sp)
   print sp
   import os.path
   filename = os.path.basename(html_path)
   this_page_index =  sp.index(filename) 
   #TODO figure out how to use url_for here: 
   html_url = '/text/' + html_path 
   page_before_exists = (not this_page_index == 0)
   page_after_exists = (not this_page_index == number_of_sister_pages)
   if page_before_exists:
      page_before = url_for('side_by_side_view',html_path = os.path.join(os.path.dirname(html_path), sp[this_page_index - 1]))
   else:
      page_before = None
   if page_after_exists:
      page_after = url_for('side_by_side_view', html_path = os.path.join(os.path.dirname(html_path), sp[this_page_index + 1]))
   else:
      page_after = None
   (text_id, page_num) = filename.split('_')
   page_num = page_num[0:-5]
   (view, date, classifier) = parse_path(html_path) 
   pagination_array = make_pagination_array(number_of_sister_pages, this_page_index, 7, html_path, sp)
   try:
      text_info = get_text_info(text_id)
      return render_template('sidebyside.html', html_path=html_url, text_info=text_info, image_path=url_for_page_image(text_id, page_num), classifier=classifier, date=date, view=view, page_num_normalized=int(page_num), page_after_exists=page_after_exists, page_before_exists=page_before_exists, page_before=page_before, page_after=page_after, pagination_array=pagination_array)
   except IOError:
      return render_template('no_such_text_id.html', textid=text_id), 404

def make_pagination_array(total, this_index, steps, html_path, sister_pages):
	import os.path
	stepsize = int(total/steps)
	pagination_array = []
	for i in range(steps):
		this_index = stepsize * i
		pagination_array.append([(this_index),url_for('side_by_side_view', html_path = os.path.join(os.path.dirname(html_path), sister_pages[this_index + 1]))])
	print pagination_array
	return pagination_array
def parse_path(textpath):
   import os.path
   last_dir = os.path.basename(os.path.dirname(textpath))
   #last_dir = os.path.dirname(textpath)
   for view in POSSIBLE_HOCR_VIEWS:
      (before, sep, after) = last_dir.partition('_' + view)
      print
      print before, sep, after
      if sep:
	      parts = before.split('_')
	      date = parts[0]
	      classifier = '_'.join(parts[1:])
	      return (view, date, classifier)
   raise ValueError("Path " + last_dir + " cannot be parsed with given views.")

def get_absolute_textpath(textpath):
   return APP_ROOT + url_for('static',filename="Texts/"+textpath )

def get_sister_pages(textpath):
   import os.path, os 
   ab_textpath = get_absolute_textpath(textpath)
   dir_contents =  os.listdir( os.path.dirname(ab_textpath) )   
   return sorted(dir_contents)
  

def textfile_exists(textpath):
   import os.path
   return os.path.isfile(get_absolute_textpath(textpath))

def textpath_for_run_details(run_details):
   return run_details['text_id'] + '/' + run_details['date'] +'_'+ run_details['classifier'] +'_'+ run_details['view'] +'/' + run_details['text_id'] + '_' + run_details['page_num'] + ".html"

def page_offset(run_details, offset):
   new_page_num = pad_page_num_for_archive(str(int(run_details['page_num']) + offset))
   run_details_copy = dict(run_details)
   run_details_copy['page_num'] = new_page_num
   print new_page_num
   return run_details_copy

def page_offset_exists(run_details, offset):
   run_details = page_offset(run_details, offset)
   return textfile_exists(textpath_for_run_details(run_details))
     
@app.route('/text/<path:textpath>')
def hello_world(textpath):
    from flask import render_template
    import lxml
    from lxml import etree
    a = get_absolute_textpath(textpath)
    print a 
    tree = etree.parse(a)
    root = tree.getroot()
    head_element = tree.xpath("/html:html/html:head | /html/head",namespaces={'html':"http://www.w3.org/1999/xhtml"})[0]
    css_file = url_for('static', filename='hocr.css')
    style = etree.SubElement(head_element, "link", rel="stylesheet", type="text/css", href=css_file)
    return etree.tostring(root, pretty_print=True)

def get_text_info(textid):
   metadata_file = open(APP_ROOT + url_for('static',filename="Metadata/" + textid + '_meta.xml'))
   info = collect_archive_text_info(metadata_file)
   return info

@app.route('/textinfo/<textid>')
def show_text_info(textid):
   from flask import render_template
   info = get_text_info(textid)
   return render_template('textinfo.html', text_info=text_info)

@app.route('/page/<path:page_path>')
def process_page(page_path):
   from flask import render_template
   return render_template('textinfo.html', name=page_path)

def collect_archive_text_info(archive_xml_file):
   from lxml import etree
   #returns dictionary with appropriate single-value strings
   info = {}
   import lxml
   categories = ['creator','title','ppi','publisher','date','identifier-access','volume']
   tree = etree.parse(archive_xml_file)
   for category in categories:
   	data = tree.xpath('/metadata/'+category+'/text()')
        try:
           info[category] = data[0]
           if len(data) > 1:
              info[category] = info[category] + ' et al.'
        except IndexError:
           info[category] = None
   return info

if __name__ == '__main__':
    app.run(debug=True)


