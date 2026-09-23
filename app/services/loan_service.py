from datetime import datetime, timedelta

from app.extensions import db
from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User

MAX_ACTIVE_LOANS = 3
DEFAULT_LOAN_DAYS = 14


class LoanNotFoundError(Exception):
    pass


class BookNotAvailableError(Exception):
    pass


class LoanLimitReachedError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def _count_active_loans(user_id):
    return Loan.query.filter_by(user_id=user_id, returned_at=None).count()


def create_loan(book_id, user_id, due_in_days=DEFAULT_LOAN_DAYS):
    book = Book.query.get(book_id)
    if book is None:
        raise BookNotFoundError(f"Book {book_id} not found")

    user = User.query.get(user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")

    if not book.available:
        raise BookNotAvailableError(f"Book {book_id} is not available")

    if _count_active_loans(user_id) >= MAX_ACTIVE_LOANS:
        raise LoanLimitReachedError(f"User {user_id} has reached the active loan limit")

    loan = Loan(
        book_id=book_id,
        user_id=user_id,
        due_date=datetime.utcnow() + timedelta(days=due_in_days),
    )
    book.available = False

    db.session.add(loan)
    db.session.commit()
    return loan


def return_loan(loan_id):
    loan = Loan.query.get(loan_id)
    if loan is None:
        raise LoanNotFoundError(f"Loan {loan_id} not found")

    loan.returned_at = datetime.utcnow()
    loan.book.available = True
    db.session.commit()
    return loan


def get_loan_by_id(loan_id):
    loan = Loan.query.get(loan_id)
    if loan is None:
        raise LoanNotFoundError(f"Loan {loan_id} not found")
    return loan


def get_loans_of_user(user_id):
    return Loan.query.filter_by(user_id=user_id).all()


def get_all_loans():
    return Loan.query.all()