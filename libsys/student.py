import mysql.connector
from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from libsys.db import get_db
from libsys.auth import login_required
from libsys.logger import log_action

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.route('/booksearch', methods=['GET', 'POST'])
@login_required
def booksearch():
    if request.method == 'POST':
        bookname = request.form['bookname'].strip()
        author = request.form['author'].strip()
        isbn = request.form['isbn'].strip()
        error = None

        if not bookname and not author and not isbn:
            error = "Require book information."
        else:
            session['book-to-search'] = {
                'bookname': bookname,
                'author': author,
                'isbn': isbn
            }
            return redirect(url_for('student.bookresult'))

        flash(error)
        return redirect(url_for('student.booksearch'))

    return render_template('student/book_search.html')

@bp.route('/bookresult', methods=['GET', 'POST'])
@login_required
def bookresult():
    db = get_db()
    c = db.cursor()
    if request.method == 'POST':
        book_id = request.form['book_id']

        u = session.get('user_id', None)
        c.execute("INSERT INTO borrows (user_id, book_id, borrow_date, return_date) "
                  "VALUES (%s, %s, %s, NULL)", 
                  (u, book_id, datetime.now().strftime("%Y/%m/%d, %H:%M:%S")))
        c.execute("UPDATE books SET copies = copies - 1 WHERE book_id = %s", (book_id,))
        db.commit()
        
        c.execute("SELECT LAST_INSERT_ID()")
        borrow_id = c.fetchone()[0]
        log_action(u, "Book Borrowed", "books", book_id, {
            "borrow_id": borrow_id,
            "borrow_date": datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        })
        
        return redirect(url_for('student.bookresult'))
    
    

    bts = session.get('book-to-search')
    books = []
    if bts is not None:
        bookname = bts['bookname']
        author = bts['author']
        isbn = bts['isbn']

        if not bookname and not author:
            c.execute("SELECT * FROM books WHERE isbn = %s ORDER BY title ASC", (isbn,))
        elif not bookname and not isbn:
            c.execute("SELECT * FROM books WHERE author = %s ORDER BY title ASC", (author,))
        elif not author and not isbn:
            c.execute("SELECT * FROM books WHERE title LIKE %s ORDER BY title ASC", ('%' + bookname + '%',))
        elif not bookname:
            c.execute("SELECT * FROM books WHERE isbn = %s and author = %s ORDER BY title ASC", 
                      (isbn, author))
        elif not author:
            c.execute("SELECT * FROM books WHERE isbn = %s and title LIKE %s ORDER BY title ASC", 
                      (isbn, '%' + bookname + '%'))
        elif not isbn:
            c.execute("SELECT * FROM books WHERE title LIKE %s and author = %s ORDER BY title ASC", 
                      ('%' + bookname + '%', author))
        else:
            c.execute("SELECT * FROM books WHERE isbn = %s and author = %s and title LIKE %s" \
            " ORDER BY title ASC", 
                      (isbn, author, '%' + bookname + '%'))

        bs = c.fetchall()
        
        for b in bs:
            books.append({
                'book_id': b[0],
                'title': b[1],
                'author': b[2],
                'year': b[3],
                'isbn': b[4],
                'copies': b[5]
            })


    return render_template('student/search_result.html', books=books)


@bp.route('/bookreturn', methods=['GET', 'POST'])
@login_required
def bookreturn():
    db = get_db()
    c = db.cursor()
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        c.execute("UPDATE borrows SET return_date = %s WHERE user_id = %s", 
                  (datetime.now().strftime("%Y/%m/%d, %H:%M:%S"), user_id))
        c.execute("UPDATE books SET copies = copies + 1 WHERE book_id = %s", (book_id,))
        db.commit()

        log_action(u, "Book Returned", "books", book_id, {
            "borrow_id": id,
            "return_date": datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        })
        return redirect(url_for('student.bookreturn'))

    u = session.get('user_id')
    c.execute("""
        SELECT
            borrows.*,
            books.title AS book_title  -- 添加书名作为新列
        FROM borrows
        INNER JOIN books 
            ON borrows.book_id = books.book_id  -- 通过 book_id 关联书籍表
        WHERE 
            borrows.user_id = %s  -- 筛选指定用户
        ORDER BY borrows.borrow_date DESC;  -- 按借阅日期降序排列（可选）
    """, (u,))

    bs = c.fetchall()
    borrows = []
    history_borrows = []
    for b in bs:
        if b[4] == None:
            borrows.append({
                'borrow_id': b[0],
                'user_id': b[1],
                'book_id': b[2],
                'borrow_date': b[3],
                'return_date': b[4],
                'title': b[5]
            })
        else:
            history_borrows.append({
                'borrow_id': b[0],
                'user_id': b[1],
                'book_id': b[2],
                'borrow_date': b[3],
                'return_date': b[4],
                'title': b[5]
            })

    return render_template('student/return.html', borrows=borrows, history_borrows=history_borrows)

@bp.route('/complaint', methods=['GET', 'POST'])
@login_required
def complaint():
    if request.method == 'POST':
        complaint_title = request.form.get('complaint_title', '').strip()
        complaint_text = request.form.get('complaint_text', '').strip()

        if not complaint_text or not complaint_text:
            flash("Please give title and text.")
            return redirect(url_for('student.complaint'))
        else:
            db = get_db()
            c = db.cursor()
            u = session.get('user_id')
            c.execute("INSERT INTO complaints (user_id, title, content, status, created_at, resolved_at, reply) VALUES " \
                      "(%s, %s, %s, %s, %s, NULL, NULL)",
                      (u, complaint_title, complaint_text, 'open', datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))
                      )
            db.commit()

            c.execute("SELECT LAST_INSERT_ID()")
            complaint_id = c.fetchone()[0]
            log_action(u, "Complaint Submitted", "complaints", complaint_id, {
                "title": complaint_title,
                "content": complaint_text
            })
            return redirect(url_for('index'))


    return render_template('student/complaint.html')