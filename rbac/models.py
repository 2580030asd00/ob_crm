from django.db import models


class Menu(models.Model):
	title = models.CharField('菜单名称', max_length=32)
	icon = models.CharField('图标', max_length=64, blank=True, null=True)
	weight = models.IntegerField('权重',default=1)

	def __str__(self):
		return self.title

class Permission(models.Model):
	"""权限表
	二级菜单
	有menu_id     表示当前的权限是 二级菜单
	没有menu_id   表示当前的权限是 普通权限

	没有parent_id  表示当前的权限是 二级菜单
	有parent_id   表示当前的权限是 普通权限
	"""
	url = models.CharField('URL地址', max_length=108)
	title = models.CharField('标题', max_length=32)
	name = models.CharField('URL的别名',max_length=32,unique=True)
	menu = models.ForeignKey('Menu', blank=True, null=True,verbose_name='所属菜单', on_delete=models.CASCADE)
	parent = models.ForeignKey('self', blank=True, null=True,verbose_name='父权限', on_delete=models.CASCADE)

	# is_menu = models.BooleanField('是否是菜单', default=False)
	# icon = models.CharField('图标', max_length=64, blank=True, null=True)

	class Meta:
		verbose_name = '权限'
		verbose_name_plural = '所有权限'

	def __str__(self):
		return self.title


class Role(models.Model):
	"""角色表"""
	name = models.CharField('角色名称', max_length=32)
	permissions = models.ManyToManyField('Permission', verbose_name='角色所拥有的权限', blank=True)

	class Meta:
		verbose_name_plural = '所有角色'

	def __str__(self):
		return self.name


class User(models.Model):
	"""用户表"""
	# name = models.CharField('用户名', max_length=32)
	# pwd = models.CharField('密码', max_length=32)
	roles = models.ManyToManyField(Role, verbose_name='用户所拥有的角色', blank=True)

	class Meta:
		verbose_name_plural = '所有用户'
		abstract = True   # 迁移的时候不生成表，继承使用  当基类

