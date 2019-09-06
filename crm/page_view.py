from django.shortcuts import HttpResponse, render, redirect, reverse
from utils.pagination import Pagination

users = [{'name': 'alex-{}'.format(i), 'password': '123'} for i in range(1, 304)]


def user_list(request):
	page = Pagination(request.GET.get('page', '1'), len(users))

	return render(request, 'user_list.html',
				  {'users': users[page.start:page.end], 'page_html': page.page_html})
