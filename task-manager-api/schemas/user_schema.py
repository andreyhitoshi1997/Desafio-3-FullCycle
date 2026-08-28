from marshmallow import Schema, fields, validate

from utils.helpers import VALID_ROLES, MIN_PASSWORD_LENGTH


class UserSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.String(
        required=True, validate=validate.Length(min=MIN_PASSWORD_LENGTH)
    )
    role = fields.String(required=False, validate=validate.OneOf(VALID_ROLES))


class UserUpdateSchema(Schema):
    name = fields.String(required=False)
    email = fields.Email(required=False)
    password = fields.String(
        required=False, validate=validate.Length(min=MIN_PASSWORD_LENGTH)
    )
    role = fields.String(required=False, validate=validate.OneOf(VALID_ROLES))
    active = fields.Boolean(required=False)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
