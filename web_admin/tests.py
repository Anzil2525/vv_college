from django.test import TestCase
from django.urls import reverse

from index.models import DepTable, LoginTable, MinorCourse, StudentReg


class MinorCourseAdminTests(TestCase):
	def setUp(self):
		self.department = DepTable.objects.create(dep='Computer Science')
		session = self.client.session
		session['type'] = 'admin'
		session.save()

	def test_add_minor_course_assigns_department(self):
		response = self.client.post(
			reverse('add_minor_course', args=[self.department.id]),
			{'course': 'Data Analytics'},
		)

		self.assertRedirects(response, reverse('view_dep'))
		minor_course = MinorCourse.objects.get(course='Data Analytics')
		self.assertEqual(minor_course.dep, self.department)

	def test_edit_minor_course_updates_name(self):
		minor_course = MinorCourse.objects.create(
			course='Data Analytics',
			dep=self.department,
		)

		response = self.client.post(
			reverse('edit_minor_course', args=[minor_course.id]),
			{'course': 'Business Analytics'},
		)

		self.assertRedirects(response, reverse('view_dep'))
		minor_course.refresh_from_db()
		self.assertEqual(minor_course.course, 'Business Analytics')

	def test_assigned_minor_course_cannot_be_deleted(self):
		minor_course = MinorCourse.objects.create(
			course='Data Analytics',
			dep=self.department,
		)
		student = StudentReg.objects.create(
			name='Student One',
			reg_no=1,
			sem=1,
			year_of_admision=2026,
			pho='1234567890',
			dep=self.department,
			minor_course=minor_course,
			login_info=LoginTable.objects.create(
				email='student@example.com',
				password='password',
				user='student',
			),
		)

		response = self.client.get(
			reverse('del_minor_course', args=[minor_course.id]),
		)

		self.assertRedirects(response, reverse('view_dep'))
		self.assertTrue(MinorCourse.objects.filter(id=minor_course.id).exists())
		self.assertEqual(student.minor_course, minor_course)
