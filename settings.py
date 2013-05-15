#settings.py
import os
# __file__ refers to the file settings.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')
#only APPEND to this list in order to ensure backward compatibility
POSSIBLE_HOCR_VIEWS = ['raw_hocr_output','combined_hocr_output','selected_hocr_output_spellchecked','selected_hocr_output','blended_hocr_output']
PREFERENCE_OF_HOCR_VIEWS=['combined_hocr_output','blended_hocr_output','selected_hocr_output_spellchecked','selected_hocr_output','raw_hocr_output']
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test2.db'#'sqlite:///' + os.path.join(APP_ROOT, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(APP_ROOT, 'db_repository')
