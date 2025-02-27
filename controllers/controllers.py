from odoo import http
from odoo.http import request, Response
from odoo.exceptions import ValidationError
import json


class StudentController(http.Controller):

    @http.route('/school_management/students', type='http', auth='none', methods=['GET'])
    def get_all_students(self):
        all_students = request.env['school_management.student'].sudo().search([])

        data = all_students.read(['id', 'name', 'standard', 'section'])

        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/school_management/students/<int:id>', type='http', auth='none', methods=['GET'])
    def get_student_by_id(self, id):
        student = request.env['school_management.student'].sudo().browse(id)

        if not student.exists():
            return request.make_response(
                json.dumps({'status': 'error', 'message': f"Student with ID {id} not found"}),
                headers=[('Content-Type', 'application/json')],
                status=404
            )

        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': {
                    'id': student.id,
                    'name': student.name,
                    'age': student.age,
                    'standard': student.standard,
                    'section': student.section
                }
            }),
            headers=[('Content-Type', 'application/json')],
            status=200
        )


    @http.route('/school_management/students/pages', type='json', auth='public', methods=['GET'])
    def get_paginated_students(self, **kwargs):
        limit = int(kwargs.get('limit', 10))
        offset = int(kwargs.get('offset', 0))

        all_students = request.env['school_management.student'].sudo().search([], limit=limit, offset=offset)

        data = all_students.read(['id', 'name', 'standard', 'section'])

        pages = request.env['school_management.student'].search_count([])

        response_data = {
            'success': True,
            'data': data,
            'pagination': {'limit':limit, 'offset':offset, 'total':pages}
        }

        return response_data


    @http.route('/school_management/students/create', auth='none', type='json', methods=['POST'])
    def create_student(self, **kw):
            data = request.httprequest.get_json()

            student = request.env['school_management.student'].sudo().create({
                'name': data['name'],
                'age': data['age']
            })

            return {
                'status': 'success',
                'message': 'Student created successfully',
                'student_id': student.id,
                'name': student.name,
                'age': student.age
            }


    @http.route('/school_management/students/update/<int:id>', auth='none', type='json', methods=['PUT'])
    def update_student(self, id):
        data = request.httprequest.get_json()

        student = request.env['school_management.student'].sudo().browse(id)
        if not student.exists():
            return {
                'status': 'error',
                'message': f"Student with ID {id} not found"
            }

        student.sudo().write({
            'name': data['name'],
            'age': data['age']
        })

        return {
            'status': 'success',
            'message': f"Student {id} updated successfully",
            'student_id':id,
            'name': student.name,
            'age': student.age
        }


    @http.route('/school_management/students/delete/<int:id>', auth='none', type='http', methods=['DELETE'], csrf=False)
    def delete_student(self, id):
        student = request.env['school_management.student'].sudo().browse(id)

        if not student.exists():
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': f"Student with ID {id} not found"
                }),
                headers=[('Content-Type', 'application/json')]
            )

        student.sudo().unlink()

        return request.make_response(
            json.dumps({
                'status': 'success',
                'message': f"Student with ID {id} deleted successfully"
            }),
            headers=[('Content-Type', 'application/json')]
        )


class SchoolManagement(http.Controller):

    @http.route('/school_management/banner', type='json', auth='user')
    def get_banner(self):
        banner_html = """
        <div class="o_kanban_view_banner" style="background-color: #f8d7da; color: #721c24; padding: 10px; border: 1px solid #f5c6cb; border-radius: 5px; text-align: center; width: 100%; box-sizing: border-box;">
            <span style="font-weight: bold;">Important Notification:</span> School Management System Update
        </div>
        """
        return {'html': banner_html}