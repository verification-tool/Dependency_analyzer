from flask import Flask, render_template, request, flash, redirect, url_for
import os
from Dependency1 import main as main1
from Dependency2 import main as main2
from Dependency3 import main as main3

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Added secret key for flash messages
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'input_file' in request.files and 'db_file' in request.files:
            # Handle file upload
            input_file = request.files['input_file']
            db_file = request.files['db_file']
            
            if input_file.filename == '' or db_file.filename == '':
                flash("Both files are required.", "error")
                return render_template('index.html')
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_file.filename)
            db_path = os.path.join(app.config['UPLOAD_FOLDER'], db_file.filename)
            
            input_file.save(input_path)
            db_file.save(db_path)
            
            # Run syntax analysis by default
            result = None
            try:
                result = main1(input_path, db_path)
            except Exception as e:
                flash(f"Error running syntax analysis: {str(e)}", "error")
            
            # Show initial UI with syntax results
            return render_template('index.html', 
                                  input_filename=input_file.filename,
                                  db_filename=db_file.filename,
                                  result=result,
                                  algorithm="Syntax",
                                  show_syntax=True)
        
        elif 'algorithm' in request.form:
            # Handle algorithm selection
            algorithm = request.form.get('algorithm')
            input_filename = request.form.get('input_filename')
            db_filename = request.form.get('db_filename')
            
            if not input_filename or not db_filename:
                flash("File names missing. Please upload again.", "error")
                return render_template('index.html')
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
            db_path = os.path.join(app.config['UPLOAD_FOLDER'], db_filename)
            
            if not os.path.exists(input_path) or not os.path.exists(db_path):
                flash("Files not found. Please upload again.", "error")
                return render_template('index.html')
            
            # Run the selected algorithm
            result = None
            show_syntax = False
            show_semantics = False
            
            try:
                if algorithm == 'syntactic':
                    result = main1(input_path, db_path)
                    show_syntax = True
                elif algorithm == 'semantic':
                    # Just show the semantic options
                    show_semantics = True
                elif algorithm == 'domain of interval':
                    result = main2(input_path, db_path)
                elif algorithm == 'polyhedra':
                    result = main3(input_path, db_path)
                else:
                    flash("Invalid algorithm selected.", "error")
                    return render_template('index.html', 
                                         input_filename=input_filename,
                                         db_filename=db_filename)
            except Exception as e:
                flash(f"Error running algorithm: {str(e)}", "error")
                return render_template('index.html', 
                                     input_filename=input_filename,
                                     db_filename=db_filename)
            
            return render_template('index.html',
                                  input_filename=input_filename,
                                  db_filename=db_filename,
                                  result=result,
                                  algorithm=algorithm.capitalize(),
                                  show_syntax=show_syntax,
                                  show_semantics=show_semantics)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
