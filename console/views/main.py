"""
Main Views | Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 12/18/2020
Updated: 8/9/2021
"""

# External imports
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView

# Internal imports
from console.settings import PROJECT_NAME as BASE
from console.state import layout, data_models
from console.utils import (
    get_model_context,
    get_page_context,
    get_user_context,
)


class ConsoleView(TemplateView):
    """Main view used for most console pages."""

    login_url = '/account/sign-in'
    redirect_field_name = 'redirect_to'

    def get_template_names(self):
        """Get the screen's template based on the URL path, where the
        URL is segmented as:
            'https://{base}/{screen}/{section}/{unit}/{part}/{piece}.
        A number of page template paths are tried, trying to match a unit
        first, then section, then a screen-section, finally a screen.
        Screen-sections and sections are also search for in a general folder.
        """
        screen = self.kwargs.get('screen', 'dashboard')
        section = self.kwargs.get('section', screen)
        unit = self.kwargs.get('unit', section)
        return [
            f'{BASE}/pages/{screen}/{unit}.html',
            f'{BASE}/pages/{screen}/{section}/{unit}.html',
            f'{BASE}/pages/{screen}/{section}.html',
            f'{BASE}/pages/{screen}/{screen}-{section}.html',
            f'{BASE}/pages/{screen}/{section}/{section}.html',
            f'{BASE}/pages/{screen}/{screen}.html',
            f'{BASE}/pages/misc/{screen}/{screen}-{section}.html',
            f'{BASE}/pages/misc/{screen}/{section}.html',
        ]

    def get_context_data(self, **kwargs):
        """Get context that is used on all pages. The context is retrieved
        dynamically from the app's state. The user's permissions
        are verified on every request. User-specific context and data
        can be returned depending on the page. Information about data
        models is provided to all pages."""
        context = super().get_context_data(**kwargs)
        context['sidebar'] = layout['sidebar']
        context['screen'] = kwargs.get('screen', '')
        context['section'] = kwargs.get('section', '')
        context['unit'] = kwargs.get('unit', '')
        organization_context = context.get('organizations')
        if not context['screen']:
            context['screen'] = 'dashboard'
            context['dashboard'] = layout['dashboard']
        elif organization_context:
            context['organization_context'] = organization_context
        context = get_page_context(self.kwargs, context)
        context = get_user_context(self.request, context)
        organizations = context.get('organizations')
        if organizations:
            context = get_model_context(context, organizations[0]['organization_id'])
        context['data_models'] = data_models
        for item in context['data_models']:
            try:
                del item['fields']
            except KeyError:
                pass
        return context


def handler404(request, *args, **argv): #pylint: disable=unused-argument
    """Handle missing pages."""
    template = f'{BASE}/pages/misc/errors/404.html'
    return render(request, template, {}, status=404)


def handler500(request, *args, **argv): #pylint: disable=unused-argument
    """Handle internal errors."""
    template = f'{BASE}/pages/misc/errors/500.html'
    return render(request, template, {}, status=500)


def no_content(request, *args, **argv): #pylint: disable=unused-argument
    """Return an empty response when needed, such as for a ping."""
    return HttpResponse(status=204)
