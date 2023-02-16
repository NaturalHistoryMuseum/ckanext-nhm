from ckan import model
from ..settings import COLLECTION_CONTACTS


def create_indexlots_email(mail_dict: dict):
    """
    Updates the given mail dict with the right details to deal with an index lots
    contact request.

    :param mail_dict: the mail dict to update
    """
    mail_dict['subject'] = 'Collection Index lot enquiry'
    mail_dict['recipient_email'] = COLLECTION_CONTACTS['Insects']
    mail_dict['recipient_name'] = 'Insects'


def create_department_email(mail_dict: dict, department: str):
    """
    Updates the given mail dict with the right details to deal with a request to contact
    the given department.

    :param mail_dict: the mail dict to update
    :param department: the department to contact
    """
    try:
        mail_dict['recipient_email'] = COLLECTION_CONTACTS[department]
    except KeyError:
        # Other/unknown etc., - so don't set recipient email
        mail_dict['body'] += f'\nDepartment: {department}\n'
    else:
        mail_dict['recipient_name'] = department
        mail_dict['body'] += (
            f'\nThe contactee has chosen to send this to the {department} '
            f'department. Our apologies if this enquiry isn\'t '
            f'relevant - please forward this onto data@nhm.ac.uk '
            f'and we will respond.\nMany thanks, Data Portal '
            f'team\n\n'
        )


def create_package_email(mail_dict: dict, package: dict):
    """
    Updates the given mail dict with the right details to contact the owner of the given
    package.

    :param mail_dict: the mail dict to update
    :param package: the package dict
    """
    # Load the user - using model rather user_show API which loads all the
    # users packages etc.,
    user_obj = model.User.get(package['creator_user_id'])
    mail_dict['recipient_name'] = user_obj.fullname or user_obj.name
    # Update send to with creator username
    mail_dict['recipient_email'] = user_obj.email

    pkg_title = package['title'] or package['name']
    mail_dict['subject'] = f'Message regarding dataset: {pkg_title}'
    mail_dict['body'] += (
        '\n\nYou have been sent this enquiry via the data portal '
        f'as you are the author of dataset {pkg_title}.  Our apologies '
        'if this isn\'t relevant - please forward this onto '
        'data@nhm.ac.uk and we will respond.\nMany thanks, '
        'Data Portal team\n\n'
    )
