from dateutil.relativedelta import relativedelta

from odoo import api, exceptions, fields, models


class EstateProperty(models.Model):
    _name = "estate.property"  # Always here goes with '.'
    _description = "The model estate.property has no access rules, consider adding one."

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=(fields.Date.today() + relativedelta(months=3)))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False, compute="_compute_selling_price")
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        default="north",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer received", "Offer Received"),
            ("offer accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
    )
    property_type_id = fields.Many2one("estate.property.type")
    buyer_id = fields.Many2one("res.partner", copy=False)
    seller_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price >= 0)", "The expected price must be positive."),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price should be positive."),
        ("unique_tag_ids", "UNIQUE(tag_ids)", "The Tag should be unique."),
        ("unique_property_type_id", "UNIQUE(property_type_id)", "The Property Type should be unique."),
    ]

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            if not record.offer_ids:
                record.best_price = 0
            else:
                record.best_price = max(record.offer_ids.mapped("price"))

    @api.depends("offer_ids")
    def _compute_selling_price(self):
        for record in self:
            if not record.offer_ids:
                record.selling_price = 0
            else:
                record.selling_price = 0
                accepted_offer = record.offer_ids.filtered(lambda e: e.status == "accepted")
                if accepted_offer:
                    record.selling_price = accepted_offer.price

    @api.onchange("garden")
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = ""
        else:
            self.garden_area = 10
            self.garden_orientation = "north"

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if (record.expected_price * 0.9) >= record.selling_price:
                raise exceptions.ValidationError_(
                    "The selling price cannot be lower than 90 percent of the expected price."
                )

    def action_cancel(self):
        for record in self:
            if record.state != "sold":
                record.state = "canceled"
            else:
                raise exceptions.UserError_("Sold properties cannot be canceled.")

    def action_sold(self):
        for record in self:
            if record.state != "canceled":
                record.state = "sold"
            else:
                raise exceptions.UserError_("Canceled properties cannot be sold.")
