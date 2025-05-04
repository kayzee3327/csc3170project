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
            key: request.form[key] for key in ['book_id', 'title', 'author', 'year', 'isbn', 'copies', 'category_id', 'category_name']
        }
        session['book-to-update'] = book
        return redirect(url_for('librarian.update'))

    
    db = get_db()
    c = db.cursor()

    c.execute('''
        SELECT 
            books.book_id, books.title, books.author, books.published_year, 
            books.isbn, books.copies, books.category_id, 
            book_categories.category_name, 
            COUNT(borrows.borrow_id) AS borrow_count
        FROM 
            books 
        LEFT JOIN 
            book_categories ON books.category_id = book_categories.category_id 
        LEFT JOIN
            borrows ON books.book_id = borrows.book_id
        GROUP BY
            books.book_id, books.title, books.author, books.published_year, 
            books.isbn, books.copies, books.category_id, book_categories.category_name
        ORDER BY 
            books.title ASC;
    ''')
    b = c.fetchall()

    books = []
    for book_row in b: # 使用不同的变量名避免混淆
        books.append({
            'book_id': book_row[0],
            'title': book_row[1],
            'author': book_row[2],
            'year': book_row[3],
            'isbn': book_row[4],
            'copies': book_row[5],
            'category_id': book_row[6],
            'category_name': book_row[7] if book_row[7] else 'Undefined',
            'borrow_count': book_row[8]
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
            'category_name': category[1]
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
    if not b:
        flash("Cannot find the book to delete")
        return redirect(url_for("librarian.catalog"))
    
    db = get_db()
    c = db.cursor()
    
    try:
        # 首先检查这本书是否有借阅记录
        c.execute("SELECT COUNT(*) FROM borrows WHERE book_id = %s", (b['book_id'],))
        borrow_count = c.fetchone()[0]
        
        if borrow_count > 0:
            flash(f"Cannot delete {b['title']}:it has {borrow_count} borrow records。Please delete these records first.")
            return redirect(url_for("librarian.catalog"))
        
        # 检查是否有预约记录
        c.execute("SELECT COUNT(*) FROM book_reservations WHERE book_id = %s", (b['book_id'],))
        reservation_count = c.fetchone()[0]
        
        if reservation_count > 0:
            flash(f"Cannot delete {b['title']}: it has {reservation_count} reservation records. Please delete these records first")
            return redirect(url_for("librarian.catalog"))
        
        # 如果没有关联记录，则可以安全删除
        c.execute("DELETE FROM books WHERE book_id = %s", (b['book_id'],))
        db.commit()
        
        log_action(g.user['user_id'], "Book Deleted", "books", b['book_id'], {
            "title": b['title'],
            "author": b['author'],
            "isbn": b['isbn']
        })
        
        flash(f"{b['title']} has been deleted successfully")
        
    except mysql.connector.errors.IntegrityError as e:
        db.rollback()
        # 提取错误详情并显示友好消息
        flash(f"Cannot delete{b['title']} : it has related records. Please delete all its borrows and reservations first.")
        
    except Exception as e:
        db.rollback()
        flash(f"Delete error: {str(e)}")
    
    return redirect(url_for("librarian.catalog"))

@bp.route('/usage', methods=['GET', 'POST'])
@admin_login_required
def usage():
    db = get_db()
    c = db.cursor()
    
    # 1. 用户借阅模式分析
    c.execute("""
        SELECT 
            u.user_id, 
            u.full_name,
            COUNT(b.borrow_id) AS total_borrows,
            AVG(DATEDIFF(b.return_date, b.borrow_date)) AS avg_borrow_days,
            COUNT(DISTINCT bc.category_id) AS different_categories_borrowed
        FROM 
            users u
        JOIN 
            borrows b ON u.user_id = b.user_id
        JOIN 
            books bk ON b.book_id = bk.book_id
        JOIN 
            book_categories bc ON bk.category_id = bc.category_id
        WHERE 
            u.role = 'student' AND b.return_date IS NOT NULL
        GROUP BY 
            u.user_id, u.full_name
        ORDER BY 
            total_borrows DESC
        LIMIT 10;
    """)
    user_patterns = []
    for row in c.fetchall():
        user_patterns.append({
            'user_id': row[0],
            'full_name': row[1],
            'total_borrows': row[2],
            'avg_borrow_days': float(row[3]) if row[3] is not None else 0,
            'different_categories': row[4]
        })
    
    # 2. 类别借阅趋势分析
    c.execute("""
        SELECT 
            bc.category_name,
            COUNT(b.borrow_id) AS borrow_count,
            COUNT(b.borrow_id) / (SELECT COUNT(*) FROM borrows) * 100 AS percentage_of_total
        FROM 
            book_categories bc
        JOIN 
            books bk ON bc.category_id = bk.category_id
        JOIN 
            borrows b ON bk.book_id = b.book_id
        GROUP BY 
            bc.category_name
        ORDER BY 
            borrow_count DESC;
    """)
    category_trends = []
    for row in c.fetchall():
        category_trends.append({
            'category_name': row[0],
            'borrow_count': row[1],
            'percentage': float(row[2]) if row[2] is not None else 0
        })
    
    # 3. 热门书籍和滞销书分析
    c.execute("""
        SELECT 
            bk.book_id,
            bk.title,
            bk.author,
            COUNT(b.borrow_id) AS borrow_count,
            bk.copies,
            COUNT(b.borrow_id) / bk.copies AS efficiency_ratio,
            DATEDIFF(NOW(), MAX(b.borrow_date)) AS days_since_last_borrow
        FROM 
            books bk
        LEFT JOIN 
            borrows b ON bk.book_id = b.book_id
        GROUP BY 
            bk.book_id, bk.title, bk.author, bk.copies
        ORDER BY 
            efficiency_ratio DESC
        LIMIT 15;
    """)
    book_popularity = []
    for row in c.fetchall():
        book_popularity.append({
            'book_id': row[0],
            'title': row[1],
            'author': row[2],
            'borrow_count': row[3],
            'copies': row[4],
            'efficiency_ratio': float(row[5]) if row[5] is not None else 0,
            'days_since_last_borrow': row[6]
        })
    
    # 5. 季节性借阅模式分析
    c.execute("""
        SELECT 
            CASE 
                WHEN MONTH(b.borrow_date) IN (12, 1, 2) THEN 'Winter'
                WHEN MONTH(b.borrow_date) IN (3, 4, 5) THEN 'Spring'
                WHEN MONTH(b.borrow_date) IN (6, 7, 8) THEN 'Summer'
                WHEN MONTH(b.borrow_date) IN (9, 10, 11) THEN 'Fall'
            END AS season,
            bc.category_name,
            COUNT(b.borrow_id) AS borrow_count
        FROM 
            borrows b
        JOIN 
            books bk ON b.book_id = bk.book_id
        JOIN 
            book_categories bc ON bk.category_id = bc.category_id
        GROUP BY 
            season, bc.category_name
        ORDER BY 
            season, borrow_count DESC;
    """)
    seasonal_patterns = []
    seasons = {'Winter': [], 'Spring': [], 'Summer': [], 'Fall': []}
    
    for row in c.fetchall():
        season = row[0]
        if season not in seasons:
            continue
        
        seasons[season].append({
            'category': row[1],
            'borrow_count': row[2]
        })
    
    # 保留原有的图书统计功能，但改名为 book_stats
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
    books_stats = []
    for book in c.fetchall():
        if book[3] is not None:
            diff = datetime.datetime.now() - book[3]
            
            books_stats.append({
                'book_id': book[0],
                'title': book[1],
                'total': book[2],
                'nearest': diff.days,
                'copies': book[4]
            })
        else:
            books_stats.append({
                'book_id': book[0],
                'title': book[1],
                'total': book[2],
                'nearest': book[3],
                'copies': book[4]
            })

    return render_template(
        'librarian/usage.html', 
        books=books_stats, 
        user_patterns=user_patterns,
        category_trends=category_trends,
        book_popularity=book_popularity,
        seasonal_patterns=seasons
    )

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
        'name': category[1],
        'description': category[2]
    }
    
    return render_template('librarian/update_category.html', category=category_dict)

@bp.route('/delete_category/<int:category_id>', methods=['POST'])
@admin_login_required
def delete_category(category_id):
    db = get_db()
    c = db.cursor()
    
    # 获取类别信息
    c.execute('SELECT category_name FROM book_categories WHERE category_id = %s', (category_id,))
    category_data = c.fetchone()
    
    if category_data is None:
        flash("Cannot find this category")
        return redirect(url_for('librarian.categories'))
        
    category_name = category_data[0]
    
    # 查询属于此分类的所有图书
    c.execute('SELECT book_id, title FROM books WHERE category_id = %s', (category_id,))
    books = c.fetchall()
    
    # 检查是否有未归还的借阅或预订
    has_constraints = False
    constraint_errors = []
    
    for book in books:
        book_id = book[0]
        
        # 检查是否有未归还的借阅
        c.execute('SELECT COUNT(*) FROM borrows WHERE book_id = %s AND return_date IS NULL', (book_id,))
        active_borrows = c.fetchone()[0]
        
        # 检查是否有未处理的预订
        c.execute('SELECT COUNT(*) FROM book_reservations WHERE book_id = %s AND status = "pending"', (book_id,))
        active_reservations = c.fetchone()[0]
        
        if active_borrows > 0 or active_reservations > 0:
            has_constraints = True
            constraint_errors.append(f"Book '{book[1]}' has {active_borrows} unreturned borrow record and {active_reservations} unhandled reservations")
    
    if has_constraints:
        error_message = "Cannot delete this category because following books have unreturned borrow record or unhandled reservations\n" + "\n".join(constraint_errors)
        flash(error_message)
        return redirect(url_for('librarian.categories'))
    
    try:
        # 开始删除操作
        for book in books:
            book_id = book[0]
            book_title = book[1]
            
            # 删除相关记录
            c.execute('DELETE FROM book_reservations WHERE book_id = %s', (book_id,))
            c.execute('DELETE FROM borrows WHERE book_id = %s', (book_id,))
            c.execute('DELETE FROM books WHERE book_id = %s', (book_id,))
            
            # 记录图书删除
            log_action(g.user['user_id'], "Book Deleted (Category Delete)", "books", book_id, {
                "title": book_title,
                "category": category_name
            })
        
        # 删除分类
        c.execute('DELETE FROM book_categories WHERE category_id = %s', (category_id,))
        
        # 提交更改
        db.commit()
        
        # 记录分类删除
        log_action(g.user['user_id'], "Category Deleted with Books", "categories", category_id, {
            "name": category_name,
            "books_deleted": len(books)
        })
        
        flash(f'Category"{category_name}"and its {len(books)}books have been deleted successfully')
    except mysql.connector.Error as e:
        db.rollback()
        flash(f'Deletion fails{e}')
    
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