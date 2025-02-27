from odoo import api, exceptions, fields, models, _
from . import utility
import xlsxwriter
import io
import base64
from datetime import datetime


class StudentExcelReportWizard(models.TransientModel):
    _name = 'student.excel.report.wizard'
    _description = 'Student Excel Report Wizard'
    _rec_name = 'display_name'

    student_id = fields.Many2one('school_management.student', string='Student')
    preview = fields.Html(string='HTML Content', readonly=True)

    def student_report(self):
        student_results = self.prepare_student_result() or "Nothing to show"
        table = utility.create_styled_table(student_results)
        self.write({
            'preview': table
        })

    def student_report_pdf(self):
        pass

    def student_report_excel(self):
        result = self.prepare_student_result()
        if result:
            """ Generate student report in Excel format """
            row = 0
            # Generate File name format
            filename = 'Student_Report.xlsx'
            # Create a workbook and add a worksheet.
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Student Report')

            # Add formatting
            header_format = workbook.add_format(
                {'bold': True, 'bg_color': '#4CAF50', 'font_color': 'white', 'align': 'center'})
            data_format = workbook.add_format({'align': 'center'})
            total_format = workbook.add_format({'bold': True, 'bg_color': '#F9F9F9', 'align': 'center'})
            top_header_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})

            # Set column widths
            worksheet.set_column(0, 0, 25)  # Course Name
            worksheet.set_column(1, 1, 15)  # Grade
            worksheet.set_column(2, 2, 10)  # Marks
            worksheet.set_column(3, 3, 20)  # Result Date
            worksheet.set_column(4, 4, 30)  # Teacher Names

            student_info = f"{self.student_id.name}'s Info"
            worksheet.merge_range(0, 0, 0, 4, student_info, top_header_format)

            # Write headers to the worksheet
            headers = ['Course Name', 'Grade', 'Marks', 'Result Date', 'Teachers']
            for col_num, header in enumerate(headers):
                worksheet.write(1, col_num, header, header_format)

            # Write data to the worksheet
            row = 2
            total_marks = 0  # For calculating the total marks

            for res in result:
                worksheet.write(row, 0, res['course_name'], data_format)
                worksheet.write(row, 1, res['grade'], data_format)
                worksheet.write(row, 2, res['marks'], data_format)
                worksheet.write(row, 3, res['result_date'].strftime('%d-%m-%Y'), data_format)
                worksheet.write(row, 4, res['teacher_names'], data_format)
                total_marks += res['marks']
                row += 1

            # Add a summary row
            worksheet.merge_range(row, 0, row, 2, 'Total Marks', total_format)
            worksheet.write(row, 3, total_marks, total_format)
            worksheet.write(row, 4, '', total_format)

            # Close the workbook
            workbook.close()
            output.seek(0)

            # Save and return the Excel file
            export_id = self.env['excel.report.out'].create(
                {'excel_file': base64.encodebytes(output.getvalue()), 'file_name': filename})
            output.close()
            return {
                'name': 'Student Report',
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'excel.report.out',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            raise exceptions.ValidationError(_('Date is not selected!'))

    def prepare_student_result(self):
        if self.student_id:
            student = self.student_id
            sql = f"""
               SELECT 
                   course.name as course_name, 
                   result.grade as grade,
                   result.marks as marks, 
                   result.result_date as result_date,
                   STRING_AGG(teacher.name, ', ') as teacher_names
               FROM school_management_student as student
               INNER JOIN school_management_result as result
                   ON student.id = result.student_id
               INNER JOIN school_management_course as course 
                   ON result.course_id = course.id
               LEFT JOIN teachers_courses_rel as rel 
                   ON course.id = rel.course_id
               LEFT JOIN school_management_teacher as teacher 
                   ON rel.teacher_id = teacher.id
               WHERE student.id = {student.id}
               GROUP BY course.name, result.grade, result.marks, result.result_date
               """
            self.env.cr.execute(sql)
            result = self.env.cr.dictfetchall()
            return result