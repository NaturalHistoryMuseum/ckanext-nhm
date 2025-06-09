def modify_field_groups(field_groups):
    """
    Given a FieldGroups object from the vds plugin, force certain field groups to show
    in multisearch results and force certain field groups to be ignored and not shown.

    :param field_groups: a FieldGroups object
    """
    # forces
    field_groups.force('artefactName')
    field_groups.force('scientificName')
    field_groups.force('')
    field_groups.force('artefactType')
    field_groups.force('associatedMediaCount')
    # ignores
    field_groups.ignore('created')
    field_groups.ignore('modified')
    field_groups.ignore('associatedMedia.*')
