from flask import render_template, request
from app import app


@app.route('/', methods=['GET', 'POST'])
def visualise():
    index = "RDSB"
    dynamic = False
    if request.method == 'POST':
        index = request.form['index']
        dynamic = True
    return render_template('visualise.html',
                           index=index,
                           dynamic=dynamic)
