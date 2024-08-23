from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "EState Property Offer"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline")

    _sql_constraints = [
        ("check_price", "CHECK(price >= 0)", "The price must be positive."),
    ]

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = relativedelta(days=record.validity) + fields.Date.today()

    def action_accept(self):
        for record in self:
            property = record.property_id
            if property:
                # Rechazar todas las demás ofertas para esta propiedad
                other_offers = self.search([("property_id", "=", property.id), ("id", "!=", record.id)])
                other_offers.write({"status": "refused"})

                # Actualizar el estado de la oferta actual a 'accepted'
                record.write({"status": "accepted"})

                # Actualizar el precio de venta de la propiedad
                property.selling_price = record.price
        return True

    def action_refuse(self):
        self.write({"status": "refused"})
        return True
