from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    nombre_usuario = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    contrasena = fields.Str(required=True, validate=validate.Length(min=6))

class CrearUsuarioSchema(Schema):
    nombre_usuario = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    contrasena = fields.Str(required=True, validate=validate.Length(min=6))
    correo = fields.Email(required=True)
    rol = fields.Str(missing='usuario', validate=validate.OneOf(["admin", "usuario"]))
