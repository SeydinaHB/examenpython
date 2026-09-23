from datetime import datetime
from marshmallow import fields

from app.extensions import ma
from app.models.loan import Loan


class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loan
        load_instance = False
        include_fk = True

    id = ma.auto_field(dump_only=True)
    book_id = ma.auto_field(required=True)
    user_id = ma.auto_field(required=True)
    borrowed_at = ma.auto_field(dump_only=True)
    due_date = ma.auto_field(dump_only=True)
    returned_at = ma.auto_field(dump_only=True)

    overdue = fields.Method("get_overdue")

    def get_overdue(self, obj):
        if obj.returned_at is not None:
            return False
        return datetime.utcnow() > obj.due_date


loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)