from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import HttpResponse, redirect
from django.conf import settings
import re


class RbacMiddleWare(MiddlewareMixin):

	def process_request(self, request):
		# 获取当前访问的URL地址
		url = request.path_info
		# 当前访问的二级菜单的ID
		request.current_menu_id = None
		# 路径导航
		request.breadcrumb_list = [{'title': '首页', 'url': '/index/'}]

		# 白名单
		for i in settings.WHITE_LIST:
			if re.match(i, url):
				return

		# 校验登录状态
		is_login = request.session.get('is_login')
		if is_login != '1':
			# 没有登录 跳转到登录页面
			return redirect(reverse('login'))

		# 判断免认证的地址
		for i in settings.NO_PERMISSION_LIST:
			if re.match(i, url):
				return

		# 获取权限信息
		permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)

		# 权限的校验
		for i in permission_dict.values():
			if re.match(r'^{}$'.format(i.get('url')), url):
				# 记录二级菜单的ID  父权限	的id
				id = i.get('id')
				pid = i.get('pid')
				pname = i.get('pname')
				if pid:
					# 当前访问的是子权限
					request.current_menu_id = pid
					p_permission = permission_dict[pname]
					request.breadcrumb_list.append({'title': p_permission['title'], 'url': p_permission['url']})

				else:
					# 当前访问的是父权限  二级菜单
					request.current_menu_id = id
				request.breadcrumb_list.append({'title':i['title'],'url':i['url']})
				return

		return HttpResponse('没有访问权限 请联系管理员')
