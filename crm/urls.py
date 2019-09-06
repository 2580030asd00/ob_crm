from django.conf.urls import url, include
from crm.views import auth
from crm.views import customer,teacher

urlpatterns = [
	url(r'^login/$', auth.login, name='login'),
	url(r'^index/$', auth.index, name='index'),
	url(r'^reg/$', auth.reg, name='reg'),

	# 公户
	url(r'^customer_list/$', customer.CustomerList.as_view(), name='customer_list'),
	# 私户
	url(r'^my_customer/$', customer.CustomerList.as_view(), name='my_customer'),

	# url(r'^add_customer/', customer.add_customer, name='add_customer'),
	# url(r'^edit_customer/(\d+)/', customer.edit_customer, name='edit_customer'),
	url(r'^add_customer/$', customer.customer_change, name='add_customer'),
	url(r'^edit_customer/(\d+)/$', customer.customer_change, name='edit_customer'),

	# 跟进记录的展示   某个销售的所有客户的跟进记录
	url(r'^consult_list/$', customer.ConsultList.as_view(), name='consult_list'),

	# 跟进记录的展示   某个客户的所有跟进记录
	url(r'^consult_list/(\d+)/$', customer.ConsultList.as_view(), name='one_consult_list'),

	# 添加跟进
	url(r'^add_consult/$', customer.add_consult, name='add_consult'),
	# 编辑跟进
	url(r'^edit_consult/(\d+)/$', customer.edit_consult, name='edit_consult'),

	url(r'^enrollment_list/$', customer.EnrollmentList.as_view(), name='enrollment_list'),

	# 添加报名表
	url(r'^add_enrollment/(?P<customer_id>\d+)$', customer.enrollment_change, name='add_enrollment'),
	# 编辑报名表
	url(r'^edit_enrollment/(?P<edit_id>\d+)/$', customer.enrollment_change, name='edit_enrollment'),

	# 班级的展示
	url(r'^class_list/$', teacher.ClassList.as_view(), name='class_list'),

	# 添加班级
	url(r'^add_class/$', teacher.class_change, name='add_class'),
	# 编辑班级
	url(r'^edit_class/(?P<edit_id>\d+)/$', teacher.class_change, name='edit_class'),

	# 展示某个班级的课程记录
	url(r'^course_record_list/(?P<class_id>\d+)$', teacher.CourseRecordList.as_view(), name='course_record_list'),

	# 添加课程记录
	url(r'^add_course_record/(?P<class_id>\d+)/$', teacher.course_record_change, name='add_course_record'),
	# 编辑课程记录
	url(r'^edit_course_record/(?P<edit_id>\d+)/$', teacher.course_record_change, name='edit_course_record'),


	# 展示某个课程记录的学习记录
	url(r'^study_record_list/(?P<course_record_id>\d+)$', teacher.study_record_list, name='study_record_list'),


]
