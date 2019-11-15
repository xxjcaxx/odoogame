# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random

class student(models.Model):
     _name = 'todo.student'
     name = fields.Char()
     phone = fields.Char()
     tasks = fields.One2many('todo.task','student')
     collaborate = fields.Many2many('todo.task')
     aleatori = fields.Char(compute='_compute_aleatori')

     @api.depends('phone')
     def _compute_aleatori(self):
         print('\033[94m Aleatori \033[0m')
         for record in self:
             record.aleatori = str(random.randint(1, 1e6))
             print('\033[94m '+record.aleatori+' \033[0m')


class task(models.Model):
    _name = 'todo.task'
    name = fields.Char()
    completed = fields.Boolean()
    date = fields.Datetime()
    student = fields.Many2one('todo.student')
    phone = fields.Char(related='student.phone')
    collaborators = fields.Many2many('todo.student')
    escaquejators = fields.Many2many('todo.student', relation='escaquejators_students',column1='task', column2='student')
