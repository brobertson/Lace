import sys
sys.stdout = sys.stderr
sys.path.insert(0, '/home/brucerob/SecretLace/Lace')
from lace import app as application
application.debug = True

