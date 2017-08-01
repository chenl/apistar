import typing  # noqa

import jinja2

from apistar.interfaces import (
    Router, Settings, StaticFiles, Template, Templates
)


class Jinja2Template(Template):
    def __init__(self, template: jinja2.Template) -> None:
        self._template = template

    def render(self, **context) -> str:
        return self._template.render(**context)


class Jinja2Templates(Templates):
    DEFAULT_SETTINGS = {
        'ROOT_DIR': None,
        'PACKAGE_DIRS': ['apistar']
    }

    def __init__(self, router: Router, statics: StaticFiles, settings: Settings) -> None:
        settings = settings.get('TEMPLATES', self.DEFAULT_SETTINGS)

        loaders = []  # type: typing.List[jinja2.BaseLoader]
        if settings['PACKAGE_DIRS']:
            loaders.extend([
                jinja2.PrefixLoader({
                    package_dir: jinja2.PackageLoader(package_dir, 'templates')
                })
                for package_dir in settings['PACKAGE_DIRS']
            ])
        if settings['ROOT_DIR']:
            loaders.append(
                jinja2.FileSystemLoader(settings['ROOT_DIR'])
            )

        loader = jinja2.ChoiceLoader(loaders)
        env = jinja2.Environment(loader=loader)
        env.globals['reverse_url'] = router.reverse_url
        env.globals['static_url'] = statics.get_url
        self._env = env

    def get_template(self, path: str) -> Template:
        template = self._env.get_template(path)
        if template is None:
            return None
        return Jinja2Template(template)
