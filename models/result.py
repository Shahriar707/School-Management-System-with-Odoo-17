from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Result(models.Model):
    _name = 'school_management.result'
    _description = 'Result'
    _inherits = {'school_management.student': 'student_id'}

    student_id = fields.Many2one('school_management.student', string='Student', required=True, ondelete='cascade')
    course_id = fields.Many2one('school_management.course', string='Course', required=True)
    grade = fields.Selection([('a+', 'A+'), ('a', 'A'), ('a-', 'A-'), ('b+', 'B+'), ('b', 'B'), ('b-', 'B-'),])
    marks = fields.Float()
    result_date = fields.Date(string='Result Date')

    @api.onchange('marks')
    def _onchange_marks(self):

        if self.marks > 150:
            raise ValidationError('Marks cannot exceed 150 for any subject.')

    @api.onchange('marks', 'course_id')
    def _onchange_total_course_marks(self):
        if not self.student_id:
            return

        total_marks = 0
        course_marks = {}

        all_records = self.student_id.result_ids | self.env['school_management.result'].new()

        for line in all_records:
            if line.course_id:
                course_marks[line.course_id.id] = line.marks or 0

        if self.course_id:
            course_marks[self.course_id.id] = self.marks or 0

        total_marks = sum(course_marks.values())
        course_count = len(course_marks)
        dynamic_limit = 150 if course_count == 1 else course_count * 100

        # Validation logic
        if total_marks > dynamic_limit:
            raise ValidationError(
                f"The total marks for the student {self.student_id.name or 'Unknown'} exceed the allowed limit of "
                f"{dynamic_limit} (Current Total: {total_marks})."
            )

    def action_click(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Result',
            'res_model': 'school_management.result',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def view_results(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Results',
            'view_mode': 'form',
            'res_model': 'school_management.result',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def print_result(self):
        return self.env.ref('school_management.school_management_school_report_action').report_action(self)

    def action_view_student(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student',
            'view_mode': 'form',
            'res_model': 'school_management.student',
            'res_id': self.student_id.id,
            'target': 'current',
        }

    def action_view_course(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Course',
            'view_mode': 'form',
            'res_model': 'school_management.course',
            'res_id': self.course_id.id,
            'target': 'current',
        }

    def action_view_results(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Results',
            'view_mode': 'tree,form',
            'res_model': 'school_management.result',
            'target': 'current',
        }