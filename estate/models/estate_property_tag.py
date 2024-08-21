from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "The model estate.property.tag has no access rules, consider adding one."

    name = fields.Char(required=True)
    