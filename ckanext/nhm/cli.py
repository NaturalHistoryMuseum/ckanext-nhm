import os
import shutil

import click

from ckan.lib.uploader import ResourceUpload
from ckan.plugins import toolkit
from .logic.schema import DATASET_TYPE_VOCABULARY

# default list of dataset category tags
DEFAULT_DATASET_CATEGORIES = [
    u'Collections',
    u'Corporate',
    u'Library and Archives',
    u'Public Engagement',
    u'Research',
    u'Citizen Science',
]


def get_commands():
    '''
    Returns the list of commands the nhm plugin exposes.

    :return: a list of click commands
    '''
    return [nhm]


def success(message, *args, **kwargs):
    '''
    Helper function that just formats the message with the given args and kwargs and then using
    click to print out the result in green.
    '''
    click.secho(message.format(*args, **kwargs), fg=u'green')


def create_context():
    '''
    Creates a new context dict with the site user set as the user and returns it.

    :return: a new context dict
    '''
    user = toolkit.get_action(u'get_site_user')({u'ignore_auth': True}, {})
    return {u'user': user[u'name']}


def get_vocabulary(context, create_if_missing=True):
    '''
    Retrieves the dataset categories vocabulary if one exists and returns it. If it doesn't exist,
    optionally creates it.

    :param context: the context dict to use when calling actions
    :param create_if_missing: whether to create the vocabulary if it doesn't exists, default: True.
    :return: the vocabulary dict or None if it doesn't exist and create_if_missing is False
    '''
    try:
        data = {u'id': DATASET_TYPE_VOCABULARY}
        return toolkit.get_action(u'vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        if create_if_missing:
            data = {u'name': DATASET_TYPE_VOCABULARY}
            vocab = toolkit.get_action(u'vocabulary_create')(context, data)
            success(u'Created new vocabulary with id {}', vocab[u'id'])
            return vocab
        return None


@click.group()
def nhm():
    '''
    The NHM CLI.
    '''
    pass


@nhm.command(name=u'create-dataset-vocabulary')
def create_dataset_vocabulary():
    '''
    Creates the dataset categories vocabulary and ensures it has the default tags in it. This
    command also updates any tags that have the same name as one of the default categories but
    differ in case (this is old behaviour that we probably don't need to have but has been carried
    over just in case).
    '''
    context = create_context()
    vocab = get_vocabulary(context)

    updated = 0
    added = 0
    for category in DEFAULT_DATASET_CATEGORIES:
        for tag in vocab[u'tags']:
            # if the category already exists as a tag, break
            if tag[u'name'] == category:
                break

            # if the category matches an existing tag but has a different case, update it
            if tag[u'name'].lower() == category.lower():
                tag[u'name'] = category
                updated += 1
                break
        else:
            # otherwise the category is completely new so add it to the tags list
            added += 1
            vocab[u'tags'].append({u'name': category, u'vocabulary_id': vocab[u'id']})

    if updated or added:
        toolkit.get_action(u'vocabulary_update')(context, vocab)
        success(u'Vocabulary tags updated: {} updated {} added', updated, added)
    else:
        success(u'Vocabulary tags already setup, no changes needed')


@nhm.command(name=u'add-dataset-category')
@click.argument(u'name')
def add_dataset_category(name):
    '''
    Adds the given name as a new category into the dataset categories vocabulary. Note that
    duplicate names aren't allowed and will be rejected (by CKAN).
    '''
    context = create_context()
    vocab = get_vocabulary(context)
    data = {u'name': name, u'vocabulary_id': vocab[u'id']}
    toolkit.get_action(u'tag_create')(context, data)
    success(u'Added {} category to dataset vocabulary', name)


@nhm.command(name=u'delete-dataset-category')
@click.argument(u'name')
def delete_dataset_category(name):
    '''
    Deletes the given name from the dataset categories vocabulary.
    '''
    context = create_context()
    vocab = get_vocabulary(context, create_if_missing=False)

    if vocab is None:
        click.secho(u"Vocabulary doesn't exist so no deletion necessary", fg=u'yellow')
        return
    else:
        tag = next(iter(filter(lambda t: t[u'name'] == name, vocab[u'tags'])), None)
        if tag is None:
            click.secho(u"Tag doesn't exist in vocabulary", fg=u'yellow')
        else:
            data = {u'id': tag[u'id'], u'vocabulary_id': vocab[u'id']}
            toolkit.get_action(u'tag_delete')(context, data)
            success(u'Deleted tag named {} [id: {}]', name, tag[u'id'])


@nhm.command(name=u'replace-resource-file')
@click.argument(u'resource-id')
@click.argument(u'path', type=click.Path(exists=True))
def replace_resource_file(resource_id, path):
    '''
    Replace the file associated with the given RESOURCE_ID with the file at PATH. If you have a file
    that is to big to upload, you can use this to replace a small dummy file with the large file.
    '''
    context = create_context()

    try:
        # check resource exists
        resource = toolkit.get_action(u'resource_show')(context, {u'id': resource_id})
    except toolkit.ObjectNotFound:
        click.secho(u'Resource {} does not exist'.format(resource_id), fg=u'red')
        raise click.Abort()

    if resource[u'url_type'] != u'upload':
        click.secho(u'No resource files available', fg=u'red')
        raise click.Abort()

    if resource.get(u'datastore_active', False):
        click.secho(u'Resource has an active datastore - cannot replace the file', fg=u'red')
        raise click.Abort()

    # get the file path
    upload = ResourceUpload(resource)
    resource_path = upload.get_path(resource[u'id'])

    resource_name = os.path.basename(resource_path)
    backup_path = os.path.join(u'/tmp', resource_name)
    # back up the file to be overwritten
    shutil.copy(resource_path, backup_path)
    # and then overwrite the file
    shutil.copy(path, resource_path)
    success(u'The download file for resource {} has been replaced with {}', resource_id, path)
    click.secho(u'A copy of the original resource file has been made at {}'.format(backup_path),
                fg=u'yellow')
