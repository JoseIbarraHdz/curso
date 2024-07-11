from odoo import fields, models

class EstateProperty(models.Model):
    _name = "estate.property" # Always here goes with '.'
    _description = 'The model estate.property has no access rules, consider adding one.'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date()
    expected_price = fields.Float(required=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    gardem_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type',
        selection=[(nort, North), (south, south), (east, East), (west, West)])
        