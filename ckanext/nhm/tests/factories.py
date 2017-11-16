#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '15/11/2017'.
"""

import factory
import mock

import ckan.model
import ckan.logic
import ckan.new_tests.helpers as helpers


class Vocabulary(factory.Factory):
    '''A factory class for creating vocabulary.'''

    FACTORY_FOR = ckan.model.Vocabulary

    # Default vocabulary params
    name = 'dataset_category'

    tags = [{'name': 'tag1'}, {'name': 'tag2'}]

    # # I'm not sure how to support factory_boy's .build() feature in CKAN,
    # # so I've disabled it here.
    # @classmethod
    # def _build(cls, target_class, *args, **kwargs):
    #     raise NotImplementedError(".build() isn't supported in CKAN")

    # To make factory_boy work with CKAN we override _create() and make it call
    # a CKAN action function.
    # We might also be able to do this by using factory_boy's direct SQLAlchemy
    # support: http://factoryboy.readthedocs.org/en/latest/orms.html#sqlalchemy
    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        if args:
            assert False, "Positional args aren't supported, use keyword args."
        vocabulary = helpers.call_action('vocabulary_create', **kwargs)


        return vocabulary
