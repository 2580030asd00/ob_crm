from crm import models
from django import forms
from django.core.exceptions import ValidationError
import hashlib


# 注册form
class RegForm(forms.ModelForm):
    password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': '您的密码'}))
    re_password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': '确认您的密码'}))

    class Meta:
        model = models.UserProfile
        fields = '__all__'  # ['字段名']  显示的字段
        exclude = ['is_active']  # 排除的字段

        labels = {'name': '用户名'}
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': '您的用户名', 'oncontextmenu': "return false"}),
            'password': forms.PasswordInput(attrs={'placeholder': 'xxxxx'}),
            'name': forms.TextInput(attrs={'placeholder': '您的真实姓名'}),
            'mobile': forms.TextInput(attrs={'placeholder': '您的手机号'}),
        }

        error_messages = {
            'username': {'invalid': '请输入正确的邮箱地址'}
        }

    def clean(self):
        self._validate_unique = True  # 校验唯一  不设置这个属性不检验唯一性
        # 获取到两次密码
        password = self.cleaned_data.get('password', )
        re_password = self.cleaned_data.get('re_password', '')
        if password == re_password:
            # 加密后返回
            md5 = hashlib.md5()
            md5.update(password.encode('utf-8'))
            password = md5.hexdigest()
            self.cleaned_data['password'] = password
            # 返回所有数据
            return self.cleaned_data
        # 抛出异常
        self.add_error('re_password', '两次密码不一致!!')
        raise ValidationError('两次密码不一致')


# bootstrap样式的form
class BootStrapModelform(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, (forms.MultipleChoiceField, forms.BooleanField)):
                continue
            field.widget.attrs['class'] = 'form-control'


# 客户form
class CustomerFrom(BootStrapModelform):
    class Meta:
        model = models.Customer
        fields = "__all__"


# 跟进记录form
class ConsultForm(BootStrapModelform):
    class Meta:
        model = models.ConsultRecord
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(self.fields['customer'])
        # print(list(self.fields['customer'].choices))
        #   self.instance.consultant  当前的用户  销售

        self.fields['customer'].choices = [('', '-----------'), ] + [(i.pk, str(i)) for i in
                                                                     self.instance.consultant.customers.all()]
        self.fields['consultant'].choices = [(self.instance.consultant.pk, self.instance.consultant)]


# 报名记录form
class EnrollmentForm(BootStrapModelform):
    class Meta:
        model = models.Enrollment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EnrollmentForm, self).__init__(*args, **kwargs)

        self.fields['customer'].choices = [(self.instance.customer_id, self.instance.customer)]


# 班级form
class ClassListForm(BootStrapModelform):
    class Meta:
        model = models.ClassList
        fields = "__all__"


# 课程记录form
class CourseRecordForm(BootStrapModelform):
    class Meta:
        model = models.CourseRecord
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CourseRecordForm, self).__init__(*args, **kwargs)

        # 限制班级为当前的班级
        self.fields['re_class'].choices = [(self.instance.re_class_id, self.instance.re_class)]
        # 限制记录者为当前的用户
        self.fields['recorder'].choices = [(self.instance.recorder_id, self.instance.recorder)]
        # 限制讲师为当前的班级的老师
        self.fields['teacher'].choices = [(teacher.pk, str(teacher)) for teacher in
                                          self.instance.re_class.teachers.all()]


# 学习记录form
class StudyRecordForm(BootStrapModelform):
    class Meta:
        model = models.StudyRecord
        fields = "__all__"
