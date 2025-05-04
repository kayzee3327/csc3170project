import mysql.connector
from datetime import datetime, timedelta

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from libsys.db import get_db
from libsys.auth import login_required
from libsys.logger import log_action

bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@bp.route('/reserve/<int:book_id>', methods=['GET', 'POST'])
@login_required
def reserve(book_id):
    """Implement book reservation functionality"""
    db = get_db()
    c = db.cursor()
    
    # Check if the book exists
    c.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = c.fetchone()
    
    if book is None:
        flash("Book not found.")
        return redirect(url_for('student.booksearch'))
    
    # Check if the user already has an active reservation for this book
    c.execute(
        "SELECT * FROM book_reservations WHERE user_id = %s AND book_id = %s AND status = 'pending'",
        (g.user['user_id'], book_id)
    )
    existing_reservation = c.fetchone()
    
    if existing_reservation:
        flash("You already have an active reservation for this book.")
        return redirect(url_for('reservations.my_reservations'))
    
    # Check if the user is currently borrowing this book
    c.execute(
        "SELECT * FROM borrows WHERE user_id = %s AND book_id = %s AND return_date IS NULL",
        (g.user['user_id'], book_id)
    )
    active_borrow = c.fetchone()
    
    if active_borrow:
        flash("You are currently borrowing this book.")
        return redirect(url_for('student.bookreturn'))
    
    if request.method == 'POST':
        # Create a new reservation with an expiry date of 7 days from now
        expiry_date = datetime.now() + timedelta(days=7)
        
        try:
            c.execute(
                "INSERT INTO book_reservations (user_id, book_id, reservation_date, expiry_date, status) VALUES (%s, %s, %s, %s, %s)",
                (g.user['user_id'], book_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                 expiry_date.strftime("%Y-%m-%d %H:%M:%S"), 'pending')
            )
            db.commit()
            flash("Book reserved successfully. Your reservation will expire in 7 days.")
            
            c.execute("SELECT LAST_INSERT_ID()")
            reservation_id = c.fetchone()[0]
            log_action(g.user['user_id'], "Book Reserved", "books", book_id, {
                "reservation_id": reservation_id,
                "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S")
            })
            return redirect(url_for('reservations.my_reservations'))
        except mysql.connector.Error as e:
            flash(f"An error occurred: {e}")
            return redirect(url_for('reservations.reserve', book_id=book_id))
    
    # Fetch book details for display
    c.execute(
        "SELECT books.*, book_categories.category_name FROM books LEFT JOIN book_categories "
        "ON books.category_id = book_categories.category_id WHERE books.book_id = %s",
        (book_id,)
    )
    book_details = c.fetchone()
    
    book_info = {
        'book_id': book_details[0],
        'title': book_details[1],
        'author': book_details[2],
        'year': book_details[3],
        'isbn': book_details[4],
        'copies': book_details[5],
        'category_id': book_details[6],
        'category_name': book_details[7] if book_details[7] else 'Undefined'
    }
    
    return render_template('reservations/reserve.html', book=book_info)

@bp.route('/my', methods=['GET'])
@login_required
def my_reservations():
    """View my reservation list"""
    db = get_db()
    c = db.cursor()
    
    # Get user's reservations with book details
    c.execute("""
        SELECT 
            r.*, 
            b.title, 
            b.author,
            b.copies
        FROM 
            book_reservations r
        JOIN 
            books b ON r.book_id = b.book_id
        WHERE 
            r.user_id = %s
        ORDER BY 
            r.reservation_date DESC
    """, (g.user['user_id'],))
    
    reservation_data = c.fetchall()
    
    reservations = []
    for r in reservation_data:
        reservations.append({
            'reservation_id': r[0],
            'user_id': r[1],
            'book_id': r[2],
            'reservation_date': r[3],
            'expiry_date': r[4],
            'status': r[5],
            'title': r[6],
            'author': r[7],
            'copies': r[8]
        })
    
    return render_template('reservations/my_reservations.html', reservations=reservations)

@bp.route('/cancel/<int:reservation_id>', methods=['POST'])
@login_required
def cancel(reservation_id):
    """Cancel reservation"""
    db = get_db()
    c = db.cursor()
    
    # Verify that the reservation belongs to the current user
    c.execute(
        "SELECT * FROM book_reservations WHERE reservation_id = %s AND user_id = %s",
        (reservation_id, g.user['user_id'])
    )
    reservation = c.fetchone()
    
    if reservation is None:
        flash("Reservation not found or does not belong to you.")
        return redirect(url_for('reservations.my_reservations'))
    
    # Cancel the reservation
    try:
        c.execute(
            "UPDATE book_reservations SET status = 'cancelled' WHERE reservation_id = %s",
            (reservation_id,)
        )
        db.commit()
        flash("Reservation cancelled successfully.")

        log_action(g.user['user_id'], "Reservation Cancelled", "books", reservation[2], {
            "reservation_id": reservation_id
        })
    except mysql.connector.Error as e:
        flash(f"An error occurred: {e}")
    
    return redirect(url_for('reservations.my_reservations'))