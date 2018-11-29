from distutils.core import setup

from self_wiki import __version__

setup(
    name='self.wiki',
    version=__version__,
    packages=['self_wiki'],
        url='https://vit.am/paulollivier/self-dot-wiki',
    license='Do Whatever You Want',
    author='Paul Ollivier',
    author_email='contact@paulollivier.fr',
    description='An opinionated wiki and todo manager',
    include_package_data=True,
    zip_safe=False,
        install_requires=['flask', 'markdown']
)
