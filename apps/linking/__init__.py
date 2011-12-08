from django.utils.translation import ugettext_lazy as _

from navigation.api import register_links, register_sidebar_template
from permissions.models import PermissionNamespace, Permission
from project_setup.api import register_setup
from documents.literals import PERMISSION_DOCUMENT_VIEW
from documents.models import Document

from linking.models import SmartLink, SmartLinkCondition

linking_namespace = PermissionNamespace('linking', _(u'Smart links'))

PERMISSION_SMART_LINK_VIEW = Permission.objects.register(linking_namespace, 'smart_link_view', _(u'View existing smart links'))
PERMISSION_SMART_LINK_CREATE = Permission.objects.register(linking_namespace, 'smart_link_create', _(u'Create new smart links'))
PERMISSION_SMART_LINK_DELETE = Permission.objects.register(linking_namespace, 'smart_link_delete', _(u'Delete smart links'))
PERMISSION_SMART_LINK_EDIT = Permission.objects.register(linking_namespace, 'smart_link_edit', _(u'Edit smart links'))

smart_link_instance_view_link = {'text': _(u'smart links actions'), 'view': 'smart_link_instance_view', 'famfam': 'page_link', 'permissions': [PERMISSION_DOCUMENT_VIEW]}
smart_link_instances_for_document = {'text': _(u'smart links'), 'view': 'smart_link_instances_for_document', 'args': 'object.pk', 'famfam': 'page_link', 'permissions': [PERMISSION_DOCUMENT_VIEW]}

smart_link_setup = {'text': _(u'smart links'), 'view': 'smart_link_list', 'icon': 'link.png', 'permissions': [PERMISSION_SMART_LINK_CREATE]}
smart_link_list = {'text': _(u'smart links list'), 'view': 'smart_link_list', 'famfam': 'link', 'permissions': [PERMISSION_SMART_LINK_CREATE]}
smart_link_create = {'text': _(u'create new smart link'), 'view': 'smart_link_create', 'famfam': 'link_add', 'permissions': [PERMISSION_SMART_LINK_CREATE]}
smart_link_edit = {'text': _(u'edit'), 'view': 'smart_link_edit', 'args': 'smart_link.pk', 'famfam': 'link_edit', 'permissions': [PERMISSION_SMART_LINK_EDIT]}
smart_link_delete = {'text': _(u'delete'), 'view': 'smart_link_delete', 'args': 'smart_link.pk', 'famfam': 'link_delete', 'permissions': [PERMISSION_SMART_LINK_DELETE]}

smart_link_condition_list = {'text': _(u'conditions'), 'view': 'smart_link_condition_list', 'args': 'smart_link.pk', 'famfam': 'cog', 'permissions': [PERMISSION_SMART_LINK_CREATE, PERMISSION_SMART_LINK_CREATE]}
smart_link_condition_create = {'text': _(u'create condition'), 'view': 'smart_link_condition_create', 'args': 'smart_link.pk', 'famfam': 'cog_add', 'permissions': [PERMISSION_SMART_LINK_CREATE, PERMISSION_SMART_LINK_EDIT]}
smart_link_condition_edit = {'text': _(u'edit'), 'view': 'smart_link_condition_edit', 'args': 'condition.pk', 'famfam': 'cog_edit', 'permissions': [PERMISSION_SMART_LINK_CREATE, PERMISSION_SMART_LINK_EDIT]}
smart_link_condition_delete = {'text': _(u'delete'), 'view': 'smart_link_condition_delete', 'args': 'condition.pk', 'famfam': 'cog_delete', 'permissions': [PERMISSION_SMART_LINK_CREATE, PERMISSION_SMART_LINK_EDIT]}

register_links(Document, [smart_link_instances_for_document], menu_name='form_header')

register_links(SmartLink, [smart_link_edit, smart_link_delete, smart_link_condition_list])
register_links(SmartLinkCondition, [smart_link_condition_edit, smart_link_condition_delete])
register_links(['smart_link_list', 'smart_link_create', 'smart_link_edit', 'smart_link_delete', 'smart_link_condition_list', 'smart_link_condition_create', 'smart_link_condition_edit', 'smart_link_condition_delete'], [smart_link_list, smart_link_create], menu_name='sidebar')
register_links(['smart_link_condition_list', 'smart_link_condition_create', 'smart_link_condition_edit', 'smart_link_condition_delete'], [smart_link_condition_create], menu_name='sidebar')

register_setup(smart_link_setup)
register_sidebar_template(['smart_link_list'], 'smart_links_help.html')