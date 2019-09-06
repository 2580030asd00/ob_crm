from django.http.request import QueryDict

class Pagination:

	def __init__(self, page_num, all_count,params=None, per_num=10, max_show=11):
		"""
		:param page_num:  当前的页码数
		:param all_count: 总数据量
		:param per_num:   每页显示的数据条数
		:param max_show:  最大显示页码数
		:param self.total_page_num:  总页码数
		:param self.page_start:  起始页码数
		:param self.page_end:    终止页码数

		"""
		try:
			page_num = int(page_num)
			if page_num <= 0:
				page_num = 1
		except Exception as e:
			page_num = 1
		self.parmas = params if params else QueryDict(mutable=True)
		self.page_num = page_num
		self.all_count = all_count
		self.per_num = per_num
		total_page_num, more = divmod(all_count, per_num)
		if more:
			total_page_num += 1
		half_show = max_show // 2
		# 总页码数不足以满足最大页码数
		if total_page_num < max_show:
			page_start = 1
			page_end = total_page_num
		else:
			if page_num - half_show <= 0:
				page_start = 1
				page_end = max_show
			elif page_num + half_show > total_page_num:
				page_start = total_page_num - max_show + 1
				page_end = total_page_num
			else:
				page_start = page_num - half_show
				page_end = page_num + half_show

		self.page_start = page_start
		self.page_end = page_end
		self.total_page_num = total_page_num

	@property
	def page_html(self):
		page_list = []
		# 上一页
		if self.page_num == 1:
			page_list.append('<li class="disabled"><a ><span>&laquo;</span></a></li>')
		else:
			#  query=alex  page = 1
			self.parmas['page'] = self.page_num - 1
			page_list.append('<li><a href="?{}" ><span>&laquo;</span></a></li>'.format(self.parmas.urlencode()))

		for i in range(self.page_start, self.page_end + 1):
			#  query=alex  page = 1
			self.parmas['page'] = i
			if i == self.page_num:
				page_list.append('<li class="active"><a href="?{}">{}</a></li>'.format(self.parmas.urlencode(), i))
			else:
				page_list.append('<li><a href="?{}">{}</a></li>'.format(self.parmas.urlencode(), i))

		# 下一页
		if self.page_num == self.total_page_num:
			page_list.append('<li class="disabled"><a><span>&raquo;</span></a></li>')
		else:
			self.parmas['page'] = self.page_num + 1   # query:alex page:2   ——》 query=alex&page=2
			page_list.append('<li><a href="?{}" ><span>&raquo;</span></a></li>'.format(self.parmas.urlencode()))

		return ''.join(page_list) if self.total_page_num else ''

	@property
	def start(self):
		return (self.page_num - 1) * self.per_num

	@property
	def end(self):
		return self.page_num * self.per_num
