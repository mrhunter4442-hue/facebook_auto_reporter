from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/targets', methods=['GET', 'POST'])
def targets():
    if request.method == 'POST':
        targets_data = request.form['targets']
        with open('targets.txt', 'w', encoding='utf-8') as f:
            f.write(targets_data)
        return "Targets saved successfully"
    
    # বিদ্যমান targets load করুন
    try:
        with open('targets.txt', 'r', encoding='utf-8') as f:
            targets_content = f.read()
    except:
        targets_content = ""
    
    return render_template('targets.html', targets=targets_content)

if __name__ == '__main__':
    app.run(debug=True)
