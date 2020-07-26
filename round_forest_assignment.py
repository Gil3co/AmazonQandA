from app import app
import os
app.run(debug=True, port=int(os.environ.get('PORT', 33507)))