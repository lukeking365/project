from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
import django.contrib.sites.requests
from django.contrib.auth import get_permission_codename
from django.contrib.admin.models import LogEntry

import xadmin
from xadmin.filters import RelatedFieldListFilter
from xadmin.filters import manager
from xadmin.layout import Row, Fieldset, Container

from .adminforms import PostAdminForm
from .models import Post, Category, Tag
from typeidea.base_admin import BaseOwnerAdmin
from typeidea.custom_site import custom_site



class PostInline(admin.TabularInline): #可以选择继承自admin.StackedInline,以获取不同的展示样式。
    form_layout = (
        Container(
            Row("title", "desc"),
        )
    )
    extra = 1  # 控制额外多几个
    model = Post

@xadmin.sites.register(Category)
class CategoryAdmin(BaseOwnerAdmin): # 原为继承admin.ModelAdmin
    # inlines = [PostInline,]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count')
    fields = ('name', 'status', 'is_nav')
    
    # def save_model(self, request, obj, form, change):
    #     obj.owner = request.user
    #     return super(CategoryAdmin, self).save_model(request, obj, form, change)
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = '文章数量'


@xadmin.sites.register(Tag)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


class CategoryOwnerFilter(admin.SimpleListFilter):
    ''' 自定义过滤器只展示当前用户分类 '''

    # title = '分类过滤器'
    # parameter_name = 'owner_category'
 
    # def lookups(self, request, model_admin):
    #     return Category.objects.filter(owner = request.user).values_list('id','name')
    
    # def queryset(self, request, queryset):
    #     category_id = self.value()
    #     if category_id:
    #         return queryset.filter(category_id=self.value())
    #     return queryset
    
    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return field.name == 'category'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        # 重新获取lookup_choices，根据owner过滤
        self.lookup_choices = Category.objects.filter(owner=request.user).values_list('id', 'name')

# PERMISSION_API = 'http://permission.sso.com/has_perm?user={}&perm_code={}' #虚拟授权网站

manager.register(CategoryOwnerFilter, take_priority=True)

@xadmin.sites.register(Post)
# @admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = [
        'title', 'category', 'status',
        'created_time','owner', 'operator'
    ]
    list_display_links = []

    list_filter = ['category',]
    search_fields = ['title', 'category__name']
    save_on_top = True

    actions_on_top = True
    actions_on_bottom = True

    # 编辑页面
    save_on_top = True
 
    exclude = ['owner',]

    # fields = (
    #     ('category','title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )
    

    form_layout = (
        Fieldset (
            '基础信息',
            Row('title','category'),
            'status',
            'tag',
        ),
        Fieldset(
            '内容信息',
            'desc',
            'content',
        )
    )

    # fieldsets = (
    #     ('基础配置',{
    #         'description':'基础配置描述',
    #         'fields':(
    #             ('title','category'),
    #             'status',
    #         ),
    #     }),
    #     ('内容',{
    #         'fields':(
    #             'desc',
    #             'content',
    #         ),
    #     }),
    #     ('额外信息',{
    #         'classes':('wide',),
    #         'fields':('tag',),
    #     }),
    # )
    # filter_horizontal = ('tag',)
    # filter_vertical = ('tag',)
    
    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('xadmin:blog_post_change', args=(obj.id,)) #admin 改为cus_admin
        )
    operator.short_description = '操作'
    
    # def has_add_permission(self, request):
    #     opts =self.opts
    #     codename = get_permission_codename('add', opts)
    #     perm_code = "%s.%s"%(opts.app_label, codename)
    #     resp = request.get(PERMISSION_API.format(request.user.username, perm_code))
    #     if resp.status_code ==200:
    #         return True
    #     else:
    #         return False


    # class Media:
    #     css = {
    #         'all':("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css",),
    #     }
    #     js = ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js",)
    
    # @property
    # def media(self):
        # # xadmin基于bootstrap，引入会页面样式冲突，仅供参考, 故注释。
        # media = super().get_media()
        # media.add_js(['https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js'])
        # media.add_css({
            # 'all': ("https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css", ),
        # })
        # return media


# @admin.register(LogEntry, site=custom_site)
# class LogEntryAdmin(admin.ModelAdmin):
#     list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
