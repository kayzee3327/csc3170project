import functools
import mysql.connector

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from libsys.db import get_db
from libsys.auth import login_required

bp = Blueprint('patron', __name__, url_prefix='/patron')

@bp.route('/booksearch', methods=['GET', 'POST'])
@login_required
def booksearch():
    if request.method == 'POST':
        pass

    return render_template('patron/book_search.html')

@bp.route('/bookreturn', methods=['GET', 'POST'])
@login_required
def bookreturn():
    if request.method == 'POST':
        pass

    return render_template('patron/return.html')

@bp.route('/complant', methods=['GET', 'POST'])
@login_required
def complaint():
    if request.method == 'POST':
        pass

    return render_template('patron/complaint.html')