from django.shortcuts import render, HttpResponse, redirect,reverse
from crm import models
import hashlib
from crm.forms import RegForm
from rbac.service.init_permission import init_permission

def index(request):
	return render(request,'index.html')


def login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		md5 = hashlib.md5()
		md5.update(password.encode('utf-8'))
		password = md5.hexdigest()
		obj = models.UserProfile.objects.filter(username=username, password=password, is_active=True).first()
		if obj:
			# 登录成功   跳转到首页
			# 进行权限信息的初始化（保存权限信息 菜单信息 登录状态）
			init_permission(request,obj)
			# 保存当前用户的ID
			request.session['pk'] = obj.pk
			return redirect(reverse('index'))
		else:
			return render(request, 'login.html', {'error': '用户名或密码错误'})

	return render(request, 'login.html')


def reg(request):
	form_obj = RegForm()
	if request.method == 'POST':
		# 把提交的数据交给form进行校验
		form_obj = RegForm(request.POST)
		if form_obj.is_valid():
			# 所有数据通过校验   保存到数据库
			# form_obj.cleaned_data.pop('re_password')
			# models.UserProfile.objects.create(**form_obj.cleaned_data)
			form_obj.save()
			return redirect('/crm/login/')

	return render(request, 'reg.html', {'form_obj': form_obj})
