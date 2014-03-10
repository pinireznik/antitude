from flask import render_template, request
from app import app


@app.route('/', methods=['GET', 'POST'])
def mitosis_web():
    return "Hiya cuntybaws"
