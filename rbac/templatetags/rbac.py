from django import template
from django.conf import settings
from collections import OrderedDict
import re

register = template.Library()


@register.inclusion_tag('rbac/menu.html')
def menu(request):
	# url = request.path_info
	order_dict = OrderedDict()

	menu_dict = request.session.get(settings.MENU_SESSION_KEY)

	# keys = sorted(menu_dict, key=lambda x: menu_dict[x]['weight'], reverse=True)
	#
	# for key in keys:
	# 	order_dict[key] = menu_dict[key]

	for key in sorted(menu_dict, key=lambda x: menu_dict[x]['weight'], reverse=True):  # [2,1]
		i = order_dict[key] = menu_dict[key]

		i['class'] = 'hide'
		for child in i.get('children'):
			if child['id'] == request.current_menu_id:
				child['class'] = 'active'
				i['class'] = ''

	return {'menu_list': order_dict.values()}


@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
	breadcrumb_list = request.breadcrumb_list
	return {'breadcrumb_list': breadcrumb_list}


@register.filter
def has_permission(request, name):
	if name in request.session[settings.PERMISSION_SESSION_KEY]:
		return True


@register.simple_tag
def gen_role_url(request, rid):
	params = request.GET.copy()
	params['rid'] = rid
	return params.urlencode()
