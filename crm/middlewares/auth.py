from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect,reverse
from crm import models


class AuthMiddleware(MiddlewareMixin):

	def process_request(self, request):

		if request.path_info in [reverse('login'),reverse('reg')]:
			return

		if request.path_info.startswith('/admin'):
			return

		pk = request.session.get('pk')

		obj = models.UserProfile.objects.filter(pk=pk).first()

		if not obj:
			# 没有登录 跳转到登录页面
			return redirect(reverse('login'))
		# 已经登录  保存obj
		request.user_obj = obj
