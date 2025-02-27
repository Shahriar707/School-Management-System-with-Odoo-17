from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo import http, _
from odoo.tools import groupby as groupbyelem
from operator import itemgetter

class MySchoolPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super(MySchoolPortal, self)._prepare_home_portal_values(counters)
        values['school_count'] = request.env['school_management.school'].search_count([])
        print("values: ", values)
        return values

    @http.route(['/my/school'], type='http', auth='user', website=True)
    def my_school_list(self, page=1, sortby=None, search=None, search_in='all', **kw):
        schools = request.env['school_management.school'].search([])
        school_count = len(schools)
        breadcrumbs = [
            ('Home', '/my/home'),
            ('Schools', '#')
        ]
        return request.render('school_management.school_list_view_template', {
            'schools': schools,
            'breadcrumbs': breadcrumbs,
            'page_name': 'my_school',
            'school_count': school_count,
        })

    @http.route(['/my/school/<int:school_id>'], type='http', auth='user', website=True)
    def my_school_detail(self, school_id, **kw):
        school = request.env['school_management.school'].browse(school_id)
        breadcrumbs = [
            ('Home', '/my/home'),
            ('Schools', '/my/school'),
            (school.name, '#')
        ]
        return request.render('school_management.school_details_view_portal', {
            'school': school,
            'breadcrumbs': breadcrumbs,
            'page_name': 'school_details',
        })

    @http.route(['/my/school/<int:school_id>/students'], type='http', auth='user', website=True)
    def my_school_student_details(self, school_id, **kw):
        school = request.env['school_management.school'].browse(school_id)
        students = request.env['school_management.student'].search([('school_id', '=', school_id)])

        return request.render('school_management.student_tree_view_template', {'school': school, 'students': students})


class MyStudentPortal(CustomerPortal):

    @http.route(['/my/student', '/my/student/page/<int:page>'], type='http', auth='user', website=True)
    def my_student_list(self, page=1, sortby=None, search=None, search_in='all', groupby="none",**kw):
        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'age': {'label': _('Age'), 'order': 'age'},
            'admission_date': {'label': _('Admission Date'), 'order': 'admission_date desc'},
        }

        search_list = {
            'all': {'label': _('All'), 'input': 'all', 'domain': []},
            'name': {'label': _('Name'), 'input': 'name', 'domain': [('name', 'ilike', search)]},
        }

        groupby_list = {
            'standard': {'label': _('Standard'), 'input': 'standard'},
            'section': {'label': _('Section'), 'input': 'section'},
            'group': {'label': _('Group'), 'input': 'group'},
        }

        if not sortby:
            sortby = 'admission_date'

        order = searchbar_sortings[sortby]['order']
        search_domain = search_list[search_in]['domain']

        student_count = request.env['school_management.student'].search_count(search_domain)

        pager = portal_pager(
            url = '/my/student',
            total = student_count,
            page = page,
            step = 10,
            scope = 5,
            url_args = {'sortby': sortby, 'search_in': search_in, 'search': search}
        )

        students = request.env['school_management.student'].search(search_domain, limit=10, offset=pager['offset'], order=order)

        breadcrumbs = [
            ('Home', '/my/home'),
            ('Schools', '#')
        ]

        if not groupby or groupby == "none":
            groupby = 'standard'

        groupby_attr = groupby_list[groupby]['input']
        grouped_students = [{groupby_attr: key, 'students': list(group)} for key, group in
                            groupbyelem(students, itemgetter(groupby_attr))] if groupby_attr else [{'students': students}]

        return request.render('school_management.student_list_view_template', {
            'students': students,
            'pager': pager,
            'sortby': sortby,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': search_list,
            'search_in': search_in,
            'search': search,
            'page_name': 'student_list',
            'group_students': grouped_students,
            'groupby': groupby,
            'searchbar_groupby': groupby_list,
            'default_url': '/my/student',
        })

    @http.route(['/my/student/<int:student_id>'], type='http', auth='user', website=True)
    def my_student_detail(self, student_id, **kw):
        student_ids = request.env['school_management.student'].search([]).ids

        student_index = student_ids.index(student_id)
        student_count = len(student_ids)

        prev_student_id = student_ids[student_index - 1] if student_index > 0 else False
        next_student_id = student_ids[student_index + 1] if student_index < student_count - 1 else False

        student = request.env['school_management.student'].sudo().browse(student_id)

        breadcrumbs = [
            ('Home', '/my/home'),
            ('Schools', '/my/school'),
            (student.name, '#')
        ]

        return request.render('school_management.student_details_view_template', {
            'student': student,
            'page_name': 'student_details',
            'prev_record': f'/my/student/{prev_student_id}' if prev_student_id else False,
            'next_record': f'/my/student/{next_student_id}' if next_student_id else False,
        })

    @http.route(['/my/student/create'], type='http', auth='user', methods=['POST', 'GET'], website=True)
    def create_student(self, **kw):
        error_list = []
        success_list = []

        schools = request.env['school_management.school'].search([])

        if request.httprequest.method == 'POST':
            keys = [
                'name', 'school_id', 'roll_number', 'standard', 'section', 'version',
                'email', 'admission_date', 'group', 'weight_in_kg', 'image'
            ]
            vals = {key: kw.get(key) for key in keys if kw.get(key)}

            if not vals.get('name'):
                error_list.append('Please enter the student name.')
            if not vals.get('school_id'):
                error_list.append('Please select a school.')
            if not vals.get('roll_number'):
                error_list.append('Please enter a roll number.')
            if not vals.get('email'):
                error_list.append('Please provide an email address.')

            if not error_list:
                new_student_id = request.env['school_management.student'].create(vals)
                if new_student_id:
                    success_list.append('Student created successfully.')

        breadcrumbs = [
            ('Home', '/my/home'),
            ('Students', '/my/student'),
            ('New Student', '#')
        ]

        return request.render('school_management.create_student_form', {
            'page_name': 'create_student',
            'schools': schools,
            'error_list': error_list,
            'success_list': success_list,
            'breadcrumbs': breadcrumbs,
        })

    @http.route(['/my/student/print/<model("school_management.student"):student_id>'], type='http', auth='user', website=True)
    def report(self, student_id, **kw):
        return self._show_report(model=student_id, report_type='pdf', report_ref='school_management.student_report_action', download=True)


    @http.route(['/my/student/update/<int:student_id>'], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def update_student(self, student_id, **kw):
        error_list = []
        success_list = []

        student = request.env['school_management.student'].sudo().browse(student_id)
        if not student:
            return request.not_found()

        schools = request.env['school_management.school'].sudo().search([])
        parents = request.env['school_management.parent'].sudo().search([])

        if request.httprequest.method == 'POST':
            keys = ['name', 'school_id', 'roll_number', 'standard', 'section', 'email', 'group',
                    'parent_id', 'admission_date', 'image']
            vals = {key: kw.get(key) for key in keys if kw.get(key)}

            if not vals.get('name'):
                error_list.append('Please enter the student name.')
            if not vals.get('school_id'):
                error_list.append('Please select a school.')

            if not error_list:
                student.write(vals)
                success_list.append('Student updated successfully.')

        breadcrumbs = [
            ('Home', '/my/home'),
            ('Students', '/my/student'),
            ('Update Student', '#')
        ]

        return request.render('school_management.update_student_form', {
            'page_name': 'update_student',
            'student': student,
            'schools': schools,
            'parents': parents,
            'error_list': error_list,
            'success_list': success_list,
            'breadcrumbs': breadcrumbs,
        })
