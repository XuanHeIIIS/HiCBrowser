
from hicbrowser import views
import sys
if len(sys.argv) > 1:
    port = int(sys.argv[2])
else:
    port = None
views.app.run(host='0.0.0.0', debug=True, port=port, processes=3)