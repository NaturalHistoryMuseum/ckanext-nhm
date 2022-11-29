import os
import shutil

import click
from ckan.lib.uploader import ResourceUpload
from ckan.plugins import toolkit

from .logic.schema import DATASET_TYPE_VOCABULARY

# default list of dataset category tags
DEFAULT_DATASET_CATEGORIES = [
    'Collections',
    'Corporate',
    'Library and Archives',
    'Public Engagement',
    'Research',
    'Citizen Science',
]


def get_commands():
    """
    Returns the list of commands the nhm plugin exposes.

    :return: a list of click commands
    """
    return [nhm]


def success(message, *args, **kwargs):
    """
    Helper function that just formats the message with the given args and kwargs and
    then using click to print out the result in green.
    """
    click.secho(message.format(*args, **kwargs), fg='green')


def create_context():
    """
    Creates a new context dict with the site user set as the user and returns it.

    :return: a new context dict
    """
    user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
    return {'user': user['name']}


def get_vocabulary(context, create_if_missing=True):
    """
    Retrieves the dataset categories vocabulary if one exists and returns it. If it
    doesn't exist, optionally creates it.

    :param context: the context dict to use when calling actions
    :param create_if_missing: whether to create the vocabulary if it doesn't exists, default: True.
    :return: the vocabulary dict or None if it doesn't exist and create_if_missing is False
    """
    try:
        data = {'id': DATASET_TYPE_VOCABULARY}
        return toolkit.get_action('vocabulary_show')(context, data)
    except toolkit.ObjectNotFound:
        if create_if_missing:
            data = {'name': DATASET_TYPE_VOCABULARY}
            vocab = toolkit.get_action('vocabulary_create')(context, data)
            success('Created new vocabulary with id {}', vocab['id'])
            return vocab
        return None


@click.group()
def nhm():
    """
    The NHM CLI.
    """
    pass


@nhm.command(name='create-dataset-vocabulary')
def create_dataset_vocabulary():
    """
    Creates the dataset categories vocabulary and ensures it has the default tags in it.

    This command also updates any tags that have the same name as one of the default
    categories but differ in case (this is old behaviour that we probably don't need to
    have but has been carried over just in case).
    """
    context = create_context()
    vocab = get_vocabulary(context)

    updated = 0
    added = 0
    for category in DEFAULT_DATASET_CATEGORIES:
        for tag in vocab['tags']:
            # if the category already exists as a tag, break
            if tag['name'] == category:
                break

            # if the category matches an existing tag but has a different case, update it
            if tag['name'].lower() == category.lower():
                tag['name'] = category
                updated += 1
                break
        else:
            # otherwise the category is completely new so add it to the tags list
            added += 1
            vocab['tags'].append({'name': category, 'vocabulary_id': vocab['id']})

    if updated or added:
        toolkit.get_action('vocabulary_update')(context, vocab)
        success('Vocabulary tags updated: {} updated {} added', updated, added)
    else:
        success('Vocabulary tags already setup, no changes needed')


@nhm.command(name='add-dataset-category')
@click.argument('name')
def add_dataset_category(name):
    """
    Adds the given name as a new category into the dataset categories vocabulary.

    Note that duplicate names aren't allowed and will be rejected (by CKAN).
    """
    context = create_context()
    vocab = get_vocabulary(context)
    data = {'name': name, 'vocabulary_id': vocab['id']}
    toolkit.get_action('tag_create')(context, data)
    success('Added {} category to dataset vocabulary', name)


@nhm.command(name='delete-dataset-category')
@click.argument('name')
def delete_dataset_category(name):
    """
    Deletes the given name from the dataset categories vocabulary.
    """
    context = create_context()
    vocab = get_vocabulary(context, create_if_missing=False)

    if vocab is None:
        click.secho("Vocabulary doesn't exist so no deletion necessary", fg='yellow')
        return
    else:
        tag = next(iter(filter(lambda t: t['name'] == name, vocab['tags'])), None)
        if tag is None:
            click.secho("Tag doesn't exist in vocabulary", fg='yellow')
        else:
            data = {'id': tag['id'], 'vocabulary_id': vocab['id']}
            toolkit.get_action('tag_delete')(context, data)
            success('Deleted tag named {} [id: {}]', name, tag['id'])


@nhm.command(name='replace-resource-file')
@click.argument('resource-id')
@click.argument('path', type=click.Path(exists=True))
def replace_resource_file(resource_id, path):
    """
    Replace the file associated with the given RESOURCE_ID with the file at PATH.

    If you have a file that is to big to upload, you can use this to replace a small
    dummy file with the large file.
    """
    context = create_context()

    try:
        # check resource exists
        resource = toolkit.get_action('resource_show')(context, {'id': resource_id})
    except toolkit.ObjectNotFound:
        click.secho('Resource {} does not exist'.format(resource_id), fg='red')
        raise click.Abort()

    if resource['url_type'] != 'upload':
        click.secho('No resource files available', fg='red')
        raise click.Abort()

    if resource.get('datastore_active', False):
        click.secho(
            'Resource has an active datastore - cannot replace the file', fg='red'
        )
        raise click.Abort()

    # get the file path
    upload = ResourceUpload(resource)
    resource_path = upload.get_path(resource['id'])

    resource_name = os.path.basename(resource_path)
    backup_path = os.path.join('/tmp', resource_name)
    # back up the file to be overwritten
    shutil.copy(resource_path, backup_path)
    # and then overwrite the file
    shutil.copy(path, resource_path)
    success(
        'The download file for resource {} has been replaced with {}', resource_id, path
    )
    click.secho(
        'A copy of the original resource file has been made at {}'.format(backup_path),
        fg='yellow',
    )
