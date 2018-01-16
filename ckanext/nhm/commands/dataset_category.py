# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-nhm
# Created by the Natural History Museum in London, UK

import re
from ckanext.nhm.logic.schema import DATASET_TYPE_VOCABULARY

from ckan.plugins import toolkit

DEFAULT_DATASET_CATEGORIES = [u'Collections', u'Corporate', u'Library and Archives',
                              u'Public Engagement', u'Research', u'Citizen Science']


class DatasetCategoryCommand(toolkit.CkanCommand):
    '''Create / Add / Delete type from the dataset type vocabulary
    
    Commands:
        paster dataset-category create-vocabulary -c <config>
        paster dataset-category create-vocabulary -c /etc/ckan/default/development.ini
    
        paster --plugin=ckanext-nhm dataset-type create-type 'Citizen Science' -c /etc/ckan/default/development.ini
        paster dataset-category delete-type specimen -c /etc/ckan/default/development.ini
    
    
    
    Where:
        <config> = path to your ckan config file
    
    The commands should be run from the ckanext-nhm directory.


    '''
    summary = __doc__.strip().split(u'\n')[0]
    usage = u'\n' + __doc__
    context = None

    def command(self):
        '''Retrieves the correct function based on input args.'''
        if not self.args or self.args[0] in [u'--help', u'-h', u'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up context
        user = toolkit.get_action(u'get_site_user')({u'ignore_auth': True}, {})
        self.context = {u'user': user[u'name']}

        cmd = self.args[0]

        if cmd == u'create-vocabulary':
            self.create_vocabulary()
        elif cmd == u'add-category':
            self.add_category()
        elif cmd == u'delete-category':
            self.delete_category()
        else:
            print u'Command %s not recognized' % cmd

    def create_vocabulary(self):
        '''Create the dataset vocabulary
        
        paster dataset-category create-vocabulary -c /etc/ckan/default/development.ini

        '''

        try:
            data = {u'id': DATASET_TYPE_VOCABULARY}
            vocab = toolkit.get_action(u'vocabulary_show')(self.context, data)
            missing_categories = [c for c in DEFAULT_DATASET_CATEGORIES if
                                  c not in [v[u'name'] for v in vocab[u'tags']]]
            updates = 0
            for c in missing_categories:
                matches = [v for v in vocab[u'tags'] if
                           re.match(u'(?i)' + c, v[u'name'])]
                if len(matches) == 0:
                    print(u"Adding tag '{0}'.".format(c))
                    self._add_tag(vocab[u'id'], c)
                else:
                    matches = matches[0]
                    try:
                        ix = vocab[u'tags'].index(matches)
                        matches[u'name'] = c
                        matches[u'display_name'] = c
                        vocab[u'tags'][ix] = matches
                        updates += 1
                        print(
                            u"Updating tag '{0}' to '{1}'.".format(matches[u'name'], c))
                    except IndexError:
                        pass
            if updates > 0:
                self._update_vocabulary(vocab)
            if len(missing_categories) == 0:
                print(
                    u'Dataset category vocabulary already exists and is up to date, skipping.')

        except toolkit.ObjectNotFound:

            print u"Creating vocab '{0}'".format(DATASET_TYPE_VOCABULARY)
            data = {u'name': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action(u'vocabulary_create')(self.context, data)

            for category in DEFAULT_DATASET_CATEGORIES:
                self._add_tag(vocabulary[u'id'], category)

    def add_category(self):
        '''Add a category to the dataset categories
        
        paster --plugin=ckanext-nhm dataset-category add-category 'Citizen Science 2' -c /etc/ckan/default/development.ini

        '''
        try:
            term = self.args[1]
        except IndexError:
            print u'Please specify the type to add'
        else:
            data = {u'id': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action(u'vocabulary_show')(self.context, data)
            self._add_tag(vocabulary[u'id'], term)

    def delete_category(self):
        '''Delete a category from the dataset categories
        
        paster --plugin=ckanext-nhm dataset-category delete-category specimen -c /etc/ckan/default/development.ini

        '''

        try:
            term = self.args[1]
        except IndexError:
            print u'Please specify the type to delete'
        else:
            data = {u'id': DATASET_TYPE_VOCABULARY}
            vocabulary = toolkit.get_action(u'vocabulary_show')(self.context, data)

            for tag in vocabulary[u'tags']:
                if tag[u'display_name'] == term:
                    print u'Deleting term %s in vocabulary %s' % (
                        tag[u'id'], vocabulary[u'id'])
                    data = {u'id': tag[u'id'], u'vocabulary_id': vocabulary[u'id']}
                    toolkit.get_action(u'tag_delete')(self.context, data)
                    break

    def _add_tag(self, vocabulary_id, tag):
        '''Add a tag to a vocabulary.

        :param vocabulary_id: the ID of the vocabulary to add to
        :param tag: the tag name

        '''
        print u"Adding tag {0} to vocab '{1}'".format(tag, DATASET_TYPE_VOCABULARY)
        data = {u'name': tag, u'vocabulary_id': vocabulary_id}
        toolkit.get_action(u'tag_create')(self.context, data)

    def _update_vocabulary(self, data):
        '''Updates a vocabulary with the given data.

        :param data: the data to use to update

        '''
        print u"Updating vocab '{0}'".format(DATASET_TYPE_VOCABULARY)
        toolkit.get_action(u'vocabulary_update')(self.context, data)
