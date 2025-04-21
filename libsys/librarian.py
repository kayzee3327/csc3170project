import mysql.connector
import datetime
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from libsys.db import get_db
from libsys.auth import admin_login_required
from libsys.logger import log_action

bp = Blueprint('librarian', __name__, url_prefix='/librarian')

@bp.route('/index', methods=['GET', 'POST'])
@admin_login_required
def index():
    if request.method == 'POST':
        pass
    return render_template('librarian/index.html')

@bp.route('/catalog', methods=['GET', 'POST'])
@admin_login_required
def catalog():
    if request.method == 'POST':
        book = {
            key: request.form[key] for key in ['book_id', 'title', 'author', 'published_year', 'isbn', 'copies']
        }
        session['book-to-update'] = book
        return redirect(url_for('librarian.update'))

    
    db = get_db()
    c = db.cursor()

    c.execute('''
        SELECT 
            books.*, 
            book_categories.category_name 
        FROM 
            books 
        LEFT JOIN 
            book_categories ON books.category_id = book_categories.category_id 
        ORDER BY 
            books.title ASC;
    ''')
    b = c.fetchall()

    books = []
    for book in b:
        books.append({
            'book_id': book[0],
            'title': book[1],
            'author': book[2],
            'year': book[3],
            'isbn': book[4],
            'copies': book[5],
            'category_id': book[6],
            'category_name': book[7] if book[7] else 'Undefined'
        })
    return render_template('librarian/catalog.html', books=books)

@bp.route('/newitem', methods=['GET', 'POST'])
@admin_login_required
def newitem():
    if request.method == 'POST':
        book = {
            key: request.form[key] for key in ['title', 'author', 'year', 'isbn', 'copies']
        }
        category_id = request.form['category']

        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO books (title, author, published_year, isbn, copies, category_id) VALUES (%s, %s, %s, %s, %s, %s)",
                  (book['title'], book['author'], book['year'], book['isbn'], book['copies'], category_id))
        db.commit()

        c.execute("SELECT LAST_INSERT_ID()")
        book_id = c.fetchone()[0]
        log_action(g.user['user_id'], "Book Added", "books", book_id, {
            "title": book['title'],
            "author": book['author'],
            "isbn": book['isbn'],
            "copies": book['copies'],
            "category_id": category_id
        })
        return redirect(url_for('librarian.catalog'))

    db = get_db()
    c = db.cursor()
    c.execute('SELECT category_id, category_name FROM book_categories ORDER BY category_name ASC')
    categories_data = c.fetchall()
    
    categories = []
    for category in categories_data:
        categories.append({
            'category_id': category[0],
            'name': category[1]
        })
    
    return render_template('librarian/newitem.html', categories=categories)

@bp.route('/update', methods=['GET', 'POST'])
@admin_login_required
def update():
    if request.method == 'POST':
        book = {
            key: request.form[key] for key in ['title', 'author', 'year', 'isbn', 'copies']
        }
        category_id = request.form['category']
        b = session.get('book-to-update')

        db = get_db()
        c = db.cursor()
        c.execute("""
            UPDATE books 
            SET 
                title = %s,
                author = %s,
                published_year = %s,
                isbn = %s,
                copies = %s,
                category_id = %s
            WHERE book_id = %s;""",
            (book['title'], book['author'], book['year'], book['isbn'], book['copies'], category_id, b['book_id'])
        )
        db.commit()
        
        log_action(g.user['user_id'], "Book Updated", "books", b['book_id'], {
            "title": book['title'],
            "author": book['author'],
            "isbn": book['isbn'],
            "copies": book['copies'],
            "category_id": category_id
        })
        return redirect(url_for('librarian.catalog'))

    b = session.get('book-to-update')
    if not b:
        return redirect(url_for('librarian.catalog'))
    
    db = get_db()
    c = db.cursor()
    c.execute('SELECT category_id FROM books WHERE book_id = %s', (b['book_id'],))
    category_result = c.fetchone()
    if category_result:
        b['category_id'] = category_result[0]
    
    c.execute('SELECT category_id, category_name FROM book_categories ORDER BY category_name ASC')
    categories_data = c.fetchall()
    
    categories = []
    for category in categories_data:
        categories.append({
            'category_id': category[0],
            'category_name': category[1]
        })
    
    return render_template('librarian/update.html', book=b, categories=categories)

@bp.route('delete', methods=['GET', 'POST'])
@admin_login_required
def delete():
    b = session.get('book-to-update')
    
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM books where book_id = %s", (b['book_id'],))
    db.commit()

    log_action(g.user['user_id'], "Book Deleted", "books", b['book_id'], {
        "title": b['title'],
        "author": b['author'],
        "isbn": b['isbn']
    })
    return redirect(url_for("librarian.catalog"))


@bp.route('/inventory', methods=['GET', 'POST'])
@admin_login_required
def inventory():
    if request.method == 'POST':
        pass
    db = get_db()
    c = db.cursor()

    c.execute('SELECT * FROM books ORDER BY title ASC;')
    b = c.fetchall()

    books = []
    for book in b:
        books.append({
            'book_id': book[0],
            'title': book[1],
            'author': book[2],
            'year': book[3],
            'isbn': book[4],
            'copies': book[5]
        })
    return render_template('librarian/inventory.html', books=books)

@bp.route('/usage', methods=['GET', 'POST'])
@admin_login_required
def usage():
    if request.method == 'POST':
        pass
    
    db = get_db()
    c = db.cursor()
    c.execute("""
        SELECT 
            books.book_id AS book_id,
            books.title,
            COUNT(borrows.borrow_id) AS borrow_count,
            MAX(borrows.borrow_date) AS latest_borrow_date,
            books.copies
        FROM books
        LEFT JOIN borrows 
            ON books.book_id = borrows.book_id
        GROUP BY books.book_id, books.title
        ORDER BY borrow_count DESC, books.title ASC;
    """)
    us = c.fetchall()

    books = []
    for u in us:
        if u[3] is not None:
            diff = datetime.datetime.now() - u[3]
            
            books.append(
                {
                    'book_id': u[0],
                    'title': u[1],
                    'total': u[2],
                    'nearest': diff.days,
                    'copies': u[4]
                }
            )
        else:
            books.append(
                {
                    'book_id': u[0],
                    'title': u[1],
                    'total': u[2],
                    'nearest': u[3],
                    'copies': u[4]
                }
            )


    return render_template('librarian/usage.html', books=books)

@bp.route('/complaints', methods=['GET', 'POST'])
@admin_login_required
def complaints():
    if request.method == 'POST':
        com = {key:request.form[key] for key in ['complaint_id', 'title', 'content']}
        session['complaint-to-reply'] = com
        return redirect(url_for('librarian.reply'))

    db = get_db()
    c = db.cursor()

    c.execute('SELECT * FROM complaints ORDER BY created_at DESC;')
    cps = c.fetchall()

    com = []
    scom = [] #solve complaints
    for cp in cps:
        if cp[4] == 'open':
            com.append(
                {
                    'complaint_id': cp[0],
                    'user_id': cp[1],
                    'title': cp[2],
                    'content': cp[3],
                    'status': cp[4],
                    'created_at': cp[5],
                    'resolved_at': cp[6],
                    'resolved_by': cp[7],
                    'reply': cp[8]
                }
            )
        else:
            scom.append(
                {
                    'complaint_id': cp[0],
                    'user_id': cp[1],
                    'title': cp[2],
                    'content': cp[3],
                    'status': cp[4],
                    'created_at': cp[5],
                    'resolved_at': cp[6],
                    'resolved_by': cp[7],
                    'reply': cp[8]
                }
            )

    return render_template('librarian/complaints.html', complaints=com, solved_complaints=scom)

@bp.route('reply', methods=['GET', 'POST'])
@admin_login_required
def reply():
    if request.method == 'POST':
        text = request.form['complaint_text']
        com = session.get('complaint-to-reply')
        
        db = get_db()
        c = db.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE complaints SET reply = %s, status = %s, resolved_at = %s, resolved_by = %s WHERE complaint_id = %s", 
                  (text, "resolved", now, g.user['user_id'], com['complaint_id']))
        db.commit()

        log_action(g.user['user_id'], "Complaint Resolved", "complaints", com['complaint_id'], {
            "reply": text,
            "resolved_at": now,
            "resolved_by": g.user['user_id']
        })
        return redirect(url_for('librarian.complaints'))


    com = session.get('complaint-to-reply')
    if not com:
        return redirect(url_for('librarian.complaints'))
    return render_template('librarian/reply.html', complaint=com)

@bp.route('/categories', methods=['GET'])
@admin_login_required
def categories():
    db = get_db()
    c = db.cursor()
    
    c.execute('SELECT * FROM book_categories ORDER BY category_name ASC;')
    categories_data = c.fetchall()
    
    categories = []
    for category in categories_data:
        c.execute('SELECT COUNT(*) FROM books WHERE category_id = %s', (category[0],))
        book_count = c.fetchone()[0]
        
        categories.append({
            'category_id': category[0],
            'name': category[1],
            'description': category[2],
            'book_count': book_count
        })
    
    return render_template('librarian/categories.html', categories=categories)

@bp.route('/new_category', methods=['GET', 'POST'])
@admin_login_required
def new_category():
    if request.method == 'POST':
        category_name = request.form['category_name'].strip()
        category_description = request.form['category_description'].strip()
        error = None
        
        if not category_name:
            error = "category name cannot be null"
        
        if error is None:
            db = get_db()
            c = db.cursor()
            
            try:
                c.execute(
                    "INSERT INTO book_categories (category_name, description) VALUES (%s, %s)",
                    (category_name, category_description)
                )
                db.commit()
                
                c.execute("SELECT LAST_INSERT_ID()")
                category_id = c.fetchone()[0]
                log_action(g.user['user_id'], "Category Added", "categories", category_id, {
                    "name": category_name,
                    "description": category_description
                })
                return redirect(url_for('librarian.categories'))
            except mysql.connector.Error as e:
                error = f"Insert category fails:{e}"
        
        flash(error)
        
    return render_template('librarian/new_category.html')

@bp.route('/update_category/<int:category_id>', methods=['GET', 'POST'])
@admin_login_required
def update_category(category_id):
    db = get_db()
    c = db.cursor()
    
    c.execute('SELECT * FROM book_categories WHERE category_id = %s', (category_id,))
    category = c.fetchone()
    
    if category is None:
        flash('Cannot find category: null')
        return redirect(url_for('librarian.categories'))
    
    if request.method == 'POST':
        category_name = request.form['category_name'].strip()
        category_description = request.form['category_description'].strip()
        error = None
        
        if not category_name:
            error = "category name cannot be null"
        
        if error is None:
            try:
                c.execute(
                    "UPDATE book_categories SET category_name = %s, description = %s WHERE category_id = %s",
                    (category_name, category_description, category_id)
                )
                db.commit()
                
                log_action(g.user['user_id'], "Category Updated", "categories", category_id, {
                "name": category_name,
                "description": category_description
                })
                return redirect(url_for('librarian.categories'))
            except mysql.connector.Error as e:
                error = f"Update category fails:{e}"
        
        flash(error)
    
    category_dict = {
        'category_id': category[0],
        'category_name': category[1],
        'category_description': category[2]
    }
    
    return render_template('librarian/update_category.html', category=category_dict)

@bp.route('/delete_category/<int:category_id>', methods=['POST'])
@admin_login_required
def delete_category(category_id):
    db = get_db()
    c = db.cursor()
    
    # 在删除前获取类别名称
    c.execute('SELECT category_name FROM book_categories WHERE category_id = %s', (category_id,))
    category_data = c.fetchone()
    
    if category_data is None:
        flash("Cannot find this category.")
        return redirect(url_for('librarian.categories'))
        
    category_name = category_data[0]
    
    c.execute('SELECT COUNT(*) FROM books WHERE category_id = %s', (category_id,))
    book_count = c.fetchone()[0]
    
    if book_count > 0:
        flash(f"Cannot delete this category because there are {book_count} books belonging to this category.")
        return redirect(url_for('librarian.categories'))
    
    try:
        c.execute('DELETE FROM book_categories WHERE category_id = %s', (category_id,))
        db.commit()
        
        log_action(g.user['user_id'], "Category Deleted", "categories", category_id, {
            "name": category_name
        })
        flash('Category has been deleted successfully')
    except mysql.connector.Error as e:
        flash(f'Category deletes fails:{e}')
    
    return redirect(url_for('librarian.categories'))

@bp.route('/logs', methods=['GET'])
@admin_login_required
def logs():
    """View system logs"""
    # Get query parameters for filtering
    action_filter = request.args.get('action', '')
    entity_type_filter = request.args.get('entity_type', '')
    date_filter = request.args.get('date', '')
    user_filter = request.args.get('user', '')
    
    db = get_db()
    c = db.cursor()
    
    # Base query
    query = """
        SELECT 
            l.log_id, 
            l.user_id, 
            u.username,
            l.action, 
            l.entity_type, 
            l.entity_id, 
            l.details, 
            l.timestamp
        FROM 
            systen_logs l
        LEFT JOIN 
            users u ON l.user_id = u.user_id
        WHERE 1=1
    """
    params = []
    
    # Add filters if provided
    if action_filter:
        query += " AND l.action LIKE %s"
        params.append(f'%{action_filter}%')
    
    if entity_type_filter:
        query += " AND l.entity_type = %s"
        params.append(entity_type_filter)
    
    if date_filter:
        query += " AND DATE(l.timestamp) = %s"
        params.append(date_filter)
    
    if user_filter:
        query += " AND (u.username LIKE %s OR u.full_name LIKE %s)"
        params.append(f'%{user_filter}%')
        params.append(f'%{user_filter}%')
    
    # Add ordering
    query += " ORDER BY l.timestamp DESC LIMIT 100"
    
    c.execute(query, params)
    log_data = c.fetchall()
    
    # Get distinct action types and entity types for filter dropdowns
    c.execute("SELECT DISTINCT action FROM systen_logs ORDER BY action")
    actions = [row[0] for row in c.fetchall()]
    
    c.execute("SELECT DISTINCT entity_type FROM systen_logs ORDER BY entity_type")
    entity_types = [row[0] for row in c.fetchall()]
    
    logs = []
    for log in log_data:
        # Parse JSON details if present
        details = json.loads(log[6]) if log[6] else {}
        
        logs.append({
            'log_id': log[0],
            'user_id': log[1],
            'username': log[2] or 'System',
            'action': log[3],
            'entity_type': log[4],
            'entity_id': log[5],
            'details': details,
            'timestamp': log[7]
        })
    
    return render_template(
        'librarian/logs.html', 
        logs=logs, 
        actions=actions, 
        entity_types=entity_types,
        filters={
            'action': action_filter,
            'entity_type': entity_type_filter,
            'date': date_filter,
            'user': user_filter
        }
    )