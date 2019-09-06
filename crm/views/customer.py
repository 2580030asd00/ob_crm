from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from crm.forms import CustomerFrom, ConsultForm, EnrollmentForm
from utils.pagination import Pagination
from django.db import transaction
from ob_crm.settings import CUSTOMER_MAX_NUM
from django.conf import settings
from django.views import View
from django.db.models import Q


# 展示客户列表 FBV
def customer_list(request):
    if request.path_info == reverse('customer_list'):
        # 获取公户（没有绑定销售的客户）
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    else:
        # 获取私户（绑定销售的客户）
        all_customer = models.Customer.objects.filter(consultant=request.user_obj)

    # 返回页面
    return render(request, 'consultant/customer_list.html', {'all_customer': all_customer})


# 展示客户列表 CBV
class CustomerList(View):
    def get(self, request, *args, **kwargs):

        q = self.search(['qq', ])  # Q(Q(qq__contains=query) | Q(name__contains=query))

        if request.path_info == reverse('customer_list'):
            # 获取公户（没有绑定销售的客户）
            all_customer = models.Customer.objects.filter(q, consultant__isnull=True)
        else:
            # 获取私户（绑定销售的客户）
            all_customer = models.Customer.objects.filter(q, consultant=request.user_obj)

        # 分页
        page = Pagination(request.GET.get('page', '1'), all_customer.count(), request.GET.copy(), 2)

        # 返回页面
        return render(request, 'consultant/customer_list.html',
                      {'all_customer': all_customer[page.start:page.end], 'page_html': page.page_html})

    def post(self, request, *args, **kwargs):

        action = request.POST.get('action')

        if hasattr(self, action):
            response = getattr(self, action)()
            if response:
                return response
        else:
            return HttpResponse('非法操作')

        # return redirect(reverse('customer_list'))
        return self.get(request, *args, **kwargs)

    def multi_apply(self):
        # 公户变私户
        ids = self.request.POST.getlist('ids')  # [ 1 2 ]

        # 判断私户的数量是否超上限
        # if len(ids) + models.Customer.objects.filter(consultant=self.request.user_obj).count()>settings.CUSTOMER_MAX_NUM:
        if len(ids) + self.request.user_obj.customers.all().count() > settings.CUSTOMER_MAX_NUM:
            return HttpResponse('差不多就行了，做人不要太贪心了！')

        try:
            with transaction.atomic():

                # 方式一
                # 先查客户   客户中改销售
                queryset = models.Customer.objects.filter(pk__in=ids,
                                                          consultant__isnull=True).select_for_update()  # 加行级锁

                if len(ids) == queryset.count():
                    # 第一个来进行操作
                    queryset.update(consultant=self.request.user_obj)
                else:
                    return HttpResponse('你申请的客户已经被别人抢走了！！你再锻炼下手速。')

        except Exception:
            pass

    # 方式二
    # 先拿用户
    # self.request.user_obj.customers.add(*models.Customer.objects.filter(pk__in=ids))

    def multi_pub(self):
        # 私户变公户
        ids = self.request.POST.getlist('ids')
        # 方式一
        # models.Customer.objects.filter(pk__in=ids).update(consultant=None)
        # 方式二
        self.request.user_obj.customers.remove(*models.Customer.objects.filter(pk__in=ids))

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'

        for field_name in filed_list:
            q.children.append(Q(('{}__contains'.format(field_name), query)))

        return q


# 添加客户
def add_customer(request):
    # 生成一个不包含数据的form
    form_obj = CustomerFrom()
    if request.method == 'POST':
        # 生成一个包含数据的form
        form_obj = CustomerFrom(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer_list'))

    return render(request, 'consultant/add_customer.html', {'form_obj': form_obj})


# 编辑客户
def edit_customer(request, edit_id):
    obj = models.Customer.objects.filter(pk=edit_id).first()
    # 生成一个包含原始的数据的form
    form_obj = CustomerFrom(instance=obj)  # 实例    类 ——》 实例化   对象 实例

    if request.method == 'POST':
        form_obj = CustomerFrom(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer_list'))

    return render(request, 'consultant/edit_customer.html', {'form_obj': form_obj})


# 新增和编辑客户
def customer_change(request, edit_id=None):
    obj = models.Customer.objects.filter(pk=edit_id).first()
    # 生成一个包含原始的数据的form
    form_obj = CustomerFrom(instance=obj)  # 实例    类 ——》 实例化   对象 实例
    if request.method == 'POST':
        form_obj = CustomerFrom(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            next = request.GET.get('next')
            return redirect(next)  # /crm/customer_list/?query=123

    title = '编辑客户' if edit_id else '添加客户'
    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


# 展示跟进记录
class ConsultList(View):

    def get(self, request, customer_id=None, *args, **kwargs):
        q = self.search([])

        if not customer_id:
            # 当前销售记录所有的跟进
            all_consult = models.ConsultRecord.objects.filter(q, consultant=request.user_obj,
                                                              delete_status=False).order_by('-date')
        else:
            # 某个客户的所有跟进记录
            all_consult = models.ConsultRecord.objects.filter(q, customer_id=customer_id, delete_status=False).order_by(
                '-date')

        page = Pagination(request.GET.get('page', '1'), all_consult.count(), request.GET.copy(), 2)

        # 返回页面
        return render(request, 'consultant/consult_list.html',
                      {'all_consult': all_consult[page.start:page.end], 'page_html': page.page_html})

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'

        for field_name in filed_list:
            q.children.append(Q(('{}__contains'.format(field_name), query)))

        return q


# 添加跟进
def add_consult(request):
    obj = models.ConsultRecord(consultant=request.user_obj)

    form_obj = ConsultForm(instance=obj)
    title = '添加跟进记录'
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list'))

    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


# 编辑跟进
def edit_consult(request, edit_id):
    obj = models.ConsultRecord.objects.filter(pk=edit_id).first()

    form_obj = ConsultForm(instance=obj)
    title = '编辑跟进记录'
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list'))
    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


# 展示报名表
class EnrollmentList(View):

    def get(self, request, *args, **kwargs):
        q = self.search([])
        # 当前销售所有客户的报名表
        all_enrollment = models.Enrollment.objects.filter(q, delete_status=False,
                                                          customer__in=request.user_obj.customers.all())
        page = Pagination(request.GET.get('page', '1'), all_enrollment.count(), request.GET.copy(), 2)

        # 返回页面
        return render(request, 'consultant/enrollment_list.html',
                      {'all_enrollment': all_enrollment[page.start:page.end], 'page_html': page.page_html})

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for field_name in filed_list:
            q.children.append(Q(('{}__contains'.format(field_name), query)))

        return q


# 添加和编辑报名表
def enrollment_change(request, customer_id=None, edit_id=None):
    obj = models.Enrollment(customer_id=customer_id) if customer_id else models.Enrollment.objects.filter(
        pk=edit_id).first()
    form_obj = EnrollmentForm(instance=obj)
    title = '添加报名表' if customer_id else '编辑报名表'

    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            return redirect(next)

    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})
