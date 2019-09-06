from django.conf import settings


def init_permission(request, user):
	# 获取权限信息
	# 去除权限为空的权限  去重
	permission_query = user.roles.filter(permissions__url__isnull=False).values(
		'permissions__url',
		'permissions__title',
		'permissions__menu_id',
		'permissions__menu__title',
		'permissions__menu__icon',
		'permissions__menu__weight',
		'permissions__id',
		'permissions__name',
		'permissions__parent_id',
		'permissions__parent__name',
	).distinct()

	# print(permission_query)
	# 权限的字典
	permission_dict = {}
	# 菜单的字典
	menu_dict = {}


	for i in permission_query:
		# 把权限信息放入到permission_list
		permission_dict[i['permissions__name']]={
			'url': i['permissions__url'],
			'title': i['permissions__title'],
			'id':i['permissions__id'],
			'pid':i['permissions__parent_id'],
			'pname':i['permissions__parent__name'],
		}

		# 构建二级菜单的数据结构
		menu_id = i.get('permissions__menu_id')
		# 没有menu_id 普通权限  不需要构建菜单的结果
		if not menu_id:
			continue

		menu_dict.setdefault(menu_id, {
			'title': i.get('permissions__menu__title'),
			'icon': i.get('permissions__menu__icon'),
			'weight': i.get('permissions__menu__weight'),
			'children': []
		})

		menu_dict[menu_id]['children'].append({
			'title': i.get('permissions__title'),
			'url': i.get('permissions__url'),
			'id': i.get('permissions__id'),
		})

	# 保存权限信息和菜单信息到session中
	request.session[settings.PERMISSION_SESSION_KEY] = permission_dict  # json序列化
	request.session[settings.MENU_SESSION_KEY] = menu_dict  # json序列化
	request.session['is_login'] = '1'
