from marshmallow import Schema, fields, validate

from utils.helpers import VALID_STATUSES, MIN_TITLE_LENGTH, MAX_TITLE_LENGTH


class TaskSchema(Schema):
    title = fields.String(
        required=True,
        validate=validate.Length(min=MIN_TITLE_LENGTH, max=MAX_TITLE_LENGTH),
    )
    description = fields.String(required=False, allow_none=True)
    status = fields.String(
        required=False, validate=validate.OneOf(VALID_STATUSES)
    )
    priority = fields.Integer(required=False, validate=validate.Range(min=1, max=5))
    user_id = fields.Integer(required=False, allow_none=True)
    category_id = fields.Integer(required=False, allow_none=True)
    due_date = fields.String(required=False, allow_none=True)
    tags = fields.Raw(required=False, allow_none=True)


class TaskUpdateSchema(TaskSchema):
    title = fields.String(
        required=False,
        validate=validate.Length(min=MIN_TITLE_LENGTH, max=MAX_TITLE_LENGTH),
    )
