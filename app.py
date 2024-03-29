from flask import Flask, render_template

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'

from views.tab1 import tab1_bp
from views.tab2 import tab2_bp
from views.tab3 import tab3_bp
from views.tab4 import tab4_bp
from views.tab5 import tab5_bp
from views.tab6 import tab6_bp


# Register blueprints
app.register_blueprint(tab1_bp)
app.register_blueprint(tab2_bp)
app.register_blueprint(tab3_bp)
app.register_blueprint(tab4_bp)
app.register_blueprint(tab5_bp)
app.register_blueprint(tab6_bp)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)


