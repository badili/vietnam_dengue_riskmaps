#!env/bin/python
from kenyan_divisions_viz import app
# Remember to put debug=False on production

app.run(debug=True, port=5003)
