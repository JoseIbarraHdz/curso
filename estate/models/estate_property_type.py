from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "The model estate.property.type has no access rules, consider adding one."

    name = fields.Char(required=True)
