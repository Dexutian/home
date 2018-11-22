from django import forms


class ProfileSearchForm(forms.Form):
    """
    概要信息搜索框
    """
    stock_abb = forms.CharField(label='股票简称', max_length=100)
    stock_code = forms.CharField(label='股票代码', max_length=100)
    start_date = forms.DateField(label='起始日期')
    end_date = forms.DateField(label='结束日期')


YEAR_IN_SCHOOL_CHOICES = (
    ('FR', 'Freshman'),
    ('SO', 'Sophomore'),
    ('JR', 'Junior'),
    ('SR', 'Senior'),
)


class ProfileActionForm(forms.Form):
    """
    概要信息操作框
    """
    action = forms.ChoiceField(choices=YEAR_IN_SCHOOL_CHOICES,)