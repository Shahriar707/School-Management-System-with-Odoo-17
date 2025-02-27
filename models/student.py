from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Student(models.Model):
    _name = 'school_management.student'
    _description = 'Student'
    _inherit = ['base.person', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('unique_roll_number', 'unique(roll_number,standard)', 'Roll number must be unique.')
    ]
    _order = 'roll_number desc'

    school_id = fields.Many2one('school_management.school', string='School')
    roll_number = fields.Char(copy=False)
    standard = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                                 ('8', '8'), ('9', '9'), ('10', '10')], copy=False)
    section = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'),])
    version = fields.Selection([('Bangla', 'Bangla'), ('English', 'English')])
    admission_date = fields.Date(string='Admission Date')
    email = fields.Char()
    group = fields.Selection([('Science', 'Science'), ('Commerce', 'Commerce'), ('Arts', 'Arts')])

    weight_in_kg = fields.Float()
    weight_in_pounds = fields.Float()

    parent_id = fields.Many2one('school_management.parent', string='Parent')
    active = fields.Boolean(default=True)
    parent_name = fields.Char(related='parent_id.name', string='Parent Name', store=True)
    image = fields.Binary(string='Image')

    result_ids = fields.One2many('school_management.result', 'student_id', string='Results')
    related_student_id = fields.Many2one('school_management.student', string='Related Student', domain="[('standard', '=', standard)]")

    total_weight_calculate_loop = fields.Float(string="Total Weight (Loop)", compute="_total_weight_loop", store=False)
    total_weight_calculate_group = fields.Float(string="Total Weight (Group)", compute="_total_weight_group", store=False)

    backup_age = fields.Integer(string="Backup Age")
    due_fees = fields.Boolean(string="Due Fees")

    user_id = fields.Many2one('res.users', string='User')


    def _get_report_base_filename(self):
        return self.name

    @api.onchange('weight_in_kg')
    def _onchange_weight_in_kg(self):
        if self.weight_in_kg:
            self.weight_in_pounds = self.weight_in_kg * 2.20462

    @api.ondelete(at_uninstall=False)
    def _unlink_if_no_result(self):

        x = self._read_group([('standard', '=', 9)], groupby=['section'], aggregates=['age:sum'],
                            having=[('age:sum', '>', 15)], offset=0, limit=None, order=None)

        y = self.read_group([('standard', '=', 9)], fields=['age:sum'], groupby=['section'], offset=0, limit=None)

        for record in self:

            z = record.search_fetch([('age', '>', 15)], ['name', 'age'])

            if record.school_id:
                raise UserError('Cannot delete a student with school.')

    @api.model
    def _assign_group(self, *args, **kwargs):
        section_mapping = {
            'A': ('Science', 'English'),
            'B': ('Commerce', 'English'),
            'C': ('Arts', 'English'),
            'D': ('Science', 'Bangla'),
            'E': ('Commerce', 'Bangla'),
            'F': ('Arts', 'Bangla')
        }

        for student in self:
            if student.standard in ['9', '10']:
                if student.section in section_mapping:
                    student.group, student.version = section_mapping[student.section]

    def action_on_click(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student',
            'res_model': 'school_management.student',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_view_results(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Results',
            'res_model': 'school_management.result',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def print_student_report(self):
        return self.env.ref('school_management.student_report_action').report_action(self)


    @api.depends('weight_in_kg')
    def _total_weight_loop(self):
        for student in self:
            total_weight = 0
            students = self.env['school_management.student'].search([('standard', '=', student.standard)])

            for single in students:
                total_weight += single.weight_in_kg or 0

            student.total_weight_calculate_loop = total_weight

    @api.depends('weight_in_kg')
    def _total_weight_group(self):
        for student in self:
            total_weight = self.env['school_management.student'].read_group(
                domain=[('standard', '=', student.standard)],
                fields=['weight_in_kg:sum'],
                groupby=[]
            )

            student.total_weight_calculate_group = total_weight[0]['weight_in_kg'] if total_weight else 0.0

    def send_email_action(self):
        self.env.ref('school_management.student_email_template').send_mail(self.id, force_send="1")

    def custom_function(self):
        pass

    def action_redirect_to_school_website(self):
        return {
            "type": "ir.actions.act_url",
            "url": "https://www.google.co.uk/",
            "target": "new",
        }

    def action_copy_age_to_backup(self):
        for record in self:
            if record.age and not record.backup_age:
                record.write({'backup_age': record.age})

    def write(self, vals):
        if self.image:
            file_size = self.with_context(bin_size=True).image
            if file_size:
                file_size = file_size.decode('utf-8')
                file_size = file_size.split(' ')
                if (file_size[1] == 'Kb' and float(file_size[0]) > 1024) or (
                        file_size[1] == 'Mb' and float(file_size[0]) > 10):
                    raise UserError('Image size cannot exceed 10 MB')
        return super(Student, self).write(vals)

    def action_update_data(self):

        return self.env.ref('school_management.student_data_update_wizard_action').read()[0]