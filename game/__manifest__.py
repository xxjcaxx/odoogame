# -*- coding: utf-8 -*-
{
    'name': "game",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wizards.xml',
        'views/views.xml',
         'views/views_aux.xml', 'views/views_wars.xml',
        'views/templates.xml', 'views/search.xml',
'views/crons.xml',
        'demo/data.xml',
        'demo/raw.xml',
        'demo/cantera.xml',
        'demo/barracks.xml',
        'demo/armory.xml',
        'demo/barn.xml', 'demo/kitchen.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}