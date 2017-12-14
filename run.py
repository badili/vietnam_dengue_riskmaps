#!env/bin/python
from dengue_map import app
# Remember to put debug=False on production

app.run(debug=True, port=5003)
