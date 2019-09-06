from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from crm.forms import ClassListForm, CourseRecordForm, StudyRecordForm
from utils.pagination import Pagination
from django.views import View
from django.db.models import Q


class BaseView(View):

    def post(self, request, *args, **kwargs):

        action = request.POST.get('action')

        if hasattr(self, action):
            response = getattr(self, action)()
            if response:
                return response
        else:
            return HttpResponse('非法操作')

        return self.get(request, *args, **kwargs)

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for field_name in filed_list:
            q.children.append(Q(('{}__contains'.format(field_name), query)))

        return q


class ClassList(BaseView):
    def get(self, request, *args, **kwargs):
        q = self.search([])

        all_class = models.ClassList.objects.filter(q)

        # 分页
        page = Pagination(request.GET.get('page', '1'), all_class.count(), request.GET.copy(), 2)

        # 返回页面
        return render(request, 'teacher/class_list.html',
                      {'all_class': all_class[page.start:page.end], 'page_html': page.page_html})


# 添加和编辑班级
def class_change(request, edit_id=None):
    obj = models.ClassList.objects.filter(pk=edit_id).first()
    form_obj = ClassListForm(instance=obj)
    title = '编辑班级' if edit_id else '添加班级'

    if request.method == 'POST':
        form_obj = ClassListForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            return redirect(next)

    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


# 展示课程记录
class CourseRecordList(BaseView):
    def get(self, request, *args, class_id, **kwargs):
        q = self.search([])

        all_course_record = models.CourseRecord.objects.filter(q, re_class_id=class_id)

        page = Pagination(request.GET.get('page', '1'), all_course_record.count(), request.GET.copy(), 2)

        # 返回页面
        return render(request, 'teacher/course_record_list.html',
                      {'all_course_record': all_course_record[page.start:page.end],
                       'page_html': page.page_html,
                       'class_id': class_id
                       })

    def multi_init(self):
        # 批量初始化学习记录
        course_record_ids = self.request.POST.get('ids', [])

        for course_record_id in course_record_ids:
            # 根据一个课程ID生成学习记录
            course_record_obj = models.CourseRecord.objects.filter(pk=course_record_id).first()
            # 找当前班级的所有学生
            students = course_record_obj.re_class.customer_set.filter(status='studying')

            # for student in students:
            # 	models.StudyRecord.objects.get_or_create(student=student,course_record_id=course_record_id)
            # 	models.StudyRecord.objects.update_or_create(student=student,course_record_id=course_record_id)

            # 批量插入
            study_record_list = []
            for student in students:
                if not models.StudyRecord.objects.filter(student=student, course_record_id=course_record_id).exists():
                    study_record_list.append(models.StudyRecord(student=student, course_record_id=course_record_id))

            models.StudyRecord.objects.bulk_create(study_record_list)


# 添加和编辑课程记录
def course_record_change(request, class_id=None, edit_id=None):
    obj = models.CourseRecord(re_class_id=class_id,
                              recorder=request.user_obj) if class_id else models.CourseRecord.objects.filter(
        pk=edit_id).first()
    form_obj = CourseRecordForm(instance=obj)
    title = '添加课程记录' if class_id else '编辑课程记录'
    if request.method == 'POST':
        form_obj = CourseRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            return redirect(next)

    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


from django.forms import modelformset_factory


# 展示和编辑学习记录
def study_record_list(request, course_record_id):
    FormSet = modelformset_factory(models.StudyRecord, form=StudyRecordForm, extra=0)  # 生产modelformset的类
    formset_obj = FormSet(queryset=models.StudyRecord.objects.filter(course_record_id=course_record_id))

    if request.method == 'POST':
        formset_obj = FormSet(data=request.POST)
        if formset_obj.is_valid():
            formset_obj.save()

    return render(request, 'teacher/study_record_list.html', {'formset_obj': formset_obj})
