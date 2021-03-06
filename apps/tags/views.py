from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from permissions.api import check_permissions
from taggit.models import Tag
from documents.models import Document
from documents.views import document_list
from common.utils import encapsulate

from tags.forms import AddTagForm, TagForm
from tags.models import TagProperties
from tags import PERMISSION_TAG_CREATE, PERMISSION_TAG_ATTACH, \
    PERMISSION_TAG_REMOVE, PERMISSION_TAG_DELETE, PERMISSION_TAG_EDIT, \
    PERMISSION_TAG_VIEW
from tags import tag_tagged_item_list as tag_tagged_item_list_link


def tag_create(request):
    #check_permissions(request.user, [PERMISSION_TAG_EDIT])
    redirect_url = reverse('tag_list')
    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', redirect_url)))

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag_name = form.cleaned_data['name']

            if tag_name in Tag.objects.values_list('name', flat=True):
                messages.error(request, _(u'Tag already exists.'))
                return HttpResponseRedirect(previous)
                            
            tag = Tag(name=tag_name)
            tag.save()
            TagProperties(tag=tag, color=form.cleaned_data['color']).save()
                                            
            messages.success(request, _(u'Tag created succesfully.'))
            return HttpResponseRedirect(redirect_url)
    else:
        form = TagForm()

    return render_to_response('generic_form.html', {
        'title': _(u'create tag'),
        'form': form,
    },
    context_instance=RequestContext(request))    


def tag_add_sidebar(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', reverse('tag_list'))))

    if request.method == 'POST':
        previous = request.META.get('HTTP_REFERER', '/')
        form = AddTagForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_tag']:
                check_permissions(request.user, [PERMISSION_TAG_CREATE])
                tag_name = form.cleaned_data['new_tag']
                if Tag.objects.filter(name=tag_name):
                    is_new = False
                else:
                    is_new = True
            elif form.cleaned_data['existing_tags']:
                check_permissions(request.user, [PERMISSION_TAG_ATTACH])
                tag_name = form.cleaned_data['existing_tags']
                is_new = False
            else:
                messages.error(request, _(u'Must choose either a new tag or an existing one.'))
                return HttpResponseRedirect(previous)

            if tag_name in document.tags.values_list('name', flat=True):
                messages.warning(request, _(u'Document is already tagged as "%s"') % tag_name)
                return HttpResponseRedirect(previous)

            document.tags.add(tag_name)

            if is_new:
                tag = Tag.objects.get(name=tag_name)
                TagProperties(tag=tag, color=form.cleaned_data['color']).save()

            messages.success(request, _(u'Tag "%s" added successfully.') % tag_name)

    return HttpResponseRedirect(previous)


def tag_add_attach(request, document_id):
    # TODO: merge with tag_add_sidebar
    document = get_object_or_404(Document, pk=document_id)

    next = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER', reverse('document_tags', args=[document.pk]))))

    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_tag']:
                check_permissions(request.user, [PERMISSION_TAG_CREATE])
                tag_name = form.cleaned_data['new_tag']
                if Tag.objects.filter(name=tag_name):
                    is_new = False
                else:
                    is_new = True
            elif form.cleaned_data['existing_tags']:
                check_permissions(request.user, [PERMISSION_TAG_ATTACH])
                tag_name = form.cleaned_data['existing_tags']
                is_new = False
            else:
                messages.error(request, _(u'Must choose either a new tag or an existing one.'))
                return HttpResponseRedirect(next)

            if tag_name in document.tags.values_list('name', flat=True):
                messages.warning(request, _(u'Document is already tagged as "%s"') % tag_name)
                return HttpResponseRedirect(next)

            document.tags.add(tag_name)

            if is_new:
                tag = Tag.objects.get(name=tag_name)
                TagProperties(tag=tag, color=form.cleaned_data['color']).save()
                messages.success(request, _(u'Tag "%s" added and attached successfully.') % tag_name)
            else:
                messages.success(request, _(u'Tag "%s" attached successfully.') % tag_name)

            return HttpResponseRedirect(next)
    else:
        form = AddTagForm()

    return render_to_response('generic_form.html', {
        'title': _(u'attach tag to: %s') % document,
        'form': form,
        'object': document,
        'next': next,
    },
    context_instance=RequestContext(request))


def tag_list(request):
    return render_to_response('generic_list.html', {
        'object_list': Tag.objects.all(),
        'title': _(u'tags'),
        'hide_link': True,
        'multi_select_as_buttons': True,
        'extra_columns': [
            {
                'name': _(u'tagged items'),
                'attribute': encapsulate(lambda x: x.taggit_taggeditem_items.count())
            }
        ]
    }, context_instance=RequestContext(request))


def tag_delete(request, tag_id=None, tag_id_list=None):
    check_permissions(request.user, [PERMISSION_TAG_DELETE])
    post_action_redirect = None

    if tag_id:
        tags = [get_object_or_404(Tag, pk=tag_id)]
        post_action_redirect = reverse('tag_list')
    elif tag_id_list:
        tags = [get_object_or_404(Tag, pk=tag_id) for tag_id in tag_id_list.split(',')]
    else:
        messages.error(request, _(u'Must provide at least one tag.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', '/')))
    next = request.POST.get('next', request.GET.get('next', post_action_redirect if post_action_redirect else request.META.get('HTTP_REFERER', '/')))

    if request.method == 'POST':
        for tag in tags:
            try:
                tag.delete()
                messages.success(request, _(u'Tag "%s" deleted successfully.') % tag)
            except Exception, e:
                messages.error(request, _(u'Error deleting tag "%(tag)s": %(error)s') % {
                    'tag': tag, 'error': e
                })

        return HttpResponseRedirect(next)

    context = {
        'object_name': _(u'tag'),
        'delete_view': True,
        'previous': previous,
        'next': next,
        'form_icon': u'tag_blue_delete.png',
    }
    if len(tags) == 1:
        context['object'] = tags[0]
        context['title'] = _(u'Are you sure you wish to delete the tag: %s?') % ', '.join([unicode(d) for d in tags])
        context['message'] = _('Will be removed from all documents.')
    elif len(tags) > 1:
        context['title'] = _(u'Are you sure you wish to delete the tags: %s?') % ', '.join([unicode(d) for d in tags])
        context['message'] = _('Will be removed from all documents.')

    return render_to_response('generic_confirm.html', context,
        context_instance=RequestContext(request))


def tag_multiple_delete(request):
    return tag_delete(
        request, tag_id_list=request.GET.get('id_list', [])
    )


def tag_edit(request, tag_id):
    check_permissions(request.user, [PERMISSION_TAG_EDIT])
    tag = get_object_or_404(Tag, pk=tag_id)

    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag.name = form.cleaned_data['name']
            tag.save()
            tag_properties = tag.tagproperties_set.get()
            tag_properties.color = form.cleaned_data['color']
            tag_properties.save()
            messages.success(request, _(u'Tag updated succesfully.'))
            return HttpResponseRedirect(reverse('tag_list'))
    else:
        form = TagForm(initial={
            'name': tag.name,
            'color': tag.tagproperties_set.get().color
        })

    return render_to_response('generic_form.html', {
        'title': _(u'edit tag: %s') % tag,
        'form': form,
        'object': tag,
        'object_name': _(u'tag'),
    },
    context_instance=RequestContext(request))


def tag_tagged_item_list(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    object_list = [tagged_item.content_object for tagged_item in tag.taggit_taggeditem_items.all()]

    return document_list(
        request,
        object_list=object_list,
        title=_('documents with the tag "%s"') % tag,
        extra_context={
            'object': tag,
            'object_name': _(u'tag'),
        }
    )


def document_tags(request, document_id):
    check_permissions(request.user, [PERMISSION_TAG_VIEW])
    document = get_object_or_404(Document, pk=document_id)

    return render_to_response('generic_list.html', {
        'title': _(u'tags for: %s') % document,
        'object_list': document.tags.all(),
        'hide_link': True,
        'navigation_object_links': [tag_tagged_item_list_link],
        'object': document,
        'document': document,
        'disable_auto_focus': True,
        'multi_select_as_buttons': True,
    },
    context_instance=RequestContext(request))


def tag_remove(request, document_id, tag_id=None, tag_id_list=None):
    check_permissions(request.user, [PERMISSION_TAG_REMOVE])

    post_action_redirect = None

    if tag_id:
        tags = [get_object_or_404(Tag, pk=tag_id)]
    elif tag_id_list:
        tags = [get_object_or_404(Tag, pk=tag_id) for tag_id in tag_id_list.split(',')]
    else:
        messages.error(request, _(u'Must provide at least one tag.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    document = get_object_or_404(Document, pk=document_id)

    previous = request.POST.get('previous', request.GET.get('previous', request.META.get('HTTP_REFERER', '/')))
    next = request.POST.get('next', request.GET.get('next', post_action_redirect if post_action_redirect else request.META.get('HTTP_REFERER', '/')))

    if request.method == 'POST':
        for tag in tags:
            try:
                document.tags.remove(tag)
                messages.success(request, _(u'Tag "%s" removed successfully.') % tag)
            except Exception, e:
                messages.error(request, _(u'Error deleting tag "%(tag)s": %(error)s') % {
                    'tag': tag, 'error': e
                })

        return HttpResponseRedirect(next)

    context = {
        'previous': previous,
        'next': next,
        'form_icon': u'tag_blue_delete.png',
        'object': document,
    }

    if len(tags) == 1:
        context['title'] = _(u'Are you sure you wish to remove the tag: %s?') % ', '.join([unicode(d) for d in tags])
    elif len(tags) > 1:
        context['title'] = _(u'Are you sure you wish to remove the tags: %s?') % ', '.join([unicode(d) for d in tags])

    return render_to_response('generic_confirm.html', context,
        context_instance=RequestContext(request))


def tag_multiple_remove(request, document_id):
    return tag_remove(request, document_id=document_id, tag_id_list=request.GET.get('id_list', []))
