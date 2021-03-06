# -*- coding: utf-8 -*-
'''blade fabfile'''

from fabric.api import prompt, local, settings, env, lcd

regup = './setup.py register sdist --format=gztar,zip upload'
nodist = 'rm -rf ./dist'
sphinxup = './setup.py upload_sphinx'


def getversion(fname):
    '''
    Get the __version__ without importing.
    '''
    for line in open(fname):
        if line.startswith('__version__'):
            return '%s.%s.%s' % eval(line[13:])


def _promptup():
    with settings(warn_only=True):
        local('hg tag "%s"' % getversion('blade/__init__.py'))
        local('hg push ssh://hg@bitbucket.org/lcrees/blade')
        local('hg push github')


def _test(val):
    truth = val in ['py26', 'py27', 'py31', 'py32', 'pypy']
    if truth is False:
        raise KeyError(val)
    return val


def tox():
    '''test blade'''
    local('tox')


def docs():
    with lcd('docs/'):
        local('make clean')
        local('make html')
        local('make linkcheck')
        local('make doctest')


def update_docs():
    docs()
    with settings(warn_only=True):
        local('hg ci -m docmerge')
        local('hg push ssh://hg@bitbucket.org/lcrees/blade')
        local('hg push github')
    local(sphinxup)


def tox_recreate():
    '''recreate blade test env'''
    prompt(
        'Enter testenv: [py26, py27, py31, py32, pypy]',
        'testenv',
        validate=_test,
    )
    local('tox --recreate -e %(testenv)s' % env)


def release():
    '''release blade'''
    docs()
    local('hg update pu')
    local('hg update next')
    local('hg merge pu; hg ci -m automerge')
    local('hg update maint')
    local('hg merge default; hg ci -m automerge')
    local('hg update default')
    local('hg merge next; hg ci -m automerge')
    local('hg update pu')
    local('hg merge default; hg ci -m automerge')
    _promptup()
    local(regup)
    local(sphinxup)
    local(nodist)


def releaser():
    '''blade releaser'''
    docs()
    _promptup()
    local(regup)
    local(sphinxup)
    local(nodist)


def inplace():
    '''in-place blade'''
    docs()
    with settings(warn_only=True):
        local('hg push ssh://hg@bitbucket.org/lcrees/blade')
        local('hg push github')
    local('./setup.py sdist --format=gztar,zip upload')
    local(sphinxup)
    local(nodist)


def release_next():
    '''release blade from next branch'''
    docs()
    local('hg update maint')
    local('hg merge default; hg ci -m automerge')
    local('hg update default')
    local('hg merge next; hg ci -m automerge')
    local('hg update next')
    local('hg merge default; hg ci -m automerge')
    _promptup()
    local(regup)
    local(sphinxup)
    local(nodist)
