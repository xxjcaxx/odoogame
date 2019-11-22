# -*- coding: utf-8 -*-
from odoo import http

# class Exc2(http.Controller):
#     @http.route('/exc2/exc2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/exc2/exc2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('exc2.listing', {
#             'root': '/exc2/exc2',
#             'objects': http.request.env['exc2.exc2'].search([]),
#         })

#     @http.route('/exc2/exc2/objects/<model("exc2.exc2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('exc2.object', {
#             'object': obj
#         })