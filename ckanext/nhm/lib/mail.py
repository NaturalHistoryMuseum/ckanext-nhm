from dataclasses import dataclass
from typing import List

from ckan.plugins import toolkit
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
        mail_dict['body'] += f'\nDepartment or team: {department}\n'
    else:
        mail_dict['recipient_name'] = department
        mail_dict['body'] += (
            f'\nThe contactee has chosen to send this to the {department} '
            f'department. Our apologies if this enquiry isn\'t '
            f'relevant - please forward this onto data@nhm.ac.uk '
            f'and we will respond.\nMany thanks, Data Portal '
            f'team\n\n'
        )


@dataclass
class Recipient:
    name: str
    email: str

    @classmethod
    def from_user(cls, user: dict) -> 'Recipient':
        name = user.get('fullname', user['name'])
        email = user.get('email')
        # if the recipient email is missing, just default to data@nhm.ac.uk
        if email is None:
            email = 'data@nhm.ac.uk'
        return Recipient(name, email)

    @classmethod
    def from_user_id(cls, user_id: str) -> 'Recipient':
        context = {'ignore_auth': True}
        user = toolkit.get_action('user_show')(context, {'id': user_id})
        return Recipient.from_user(user)

    def __iter__(self):
        return iter((self.name, self.email))


def get_package_owners(package: dict) -> List[Recipient]:
    """
    Retrieve a list of the package owners for emailing.

    Owners are defined as the package admins, or if no admins are specified, the
    original creator of the package.

    :param package: the package dict
    """
    maintainer_name = package.get('maintainer', 'Maintainer')
    maintainer_email = package.get('maintainer_email')

    collaborators = toolkit.get_action('package_collaborator_list')(
        # ignore auth to ensure we can access the list of collaborators
        {'ignore_auth': True},
        # only email admins
        {'id': package['id'], 'capacity': 'admin'},
    )

    recipients = []
    if maintainer_email:
        recipients.append(Recipient(maintainer_name, maintainer_email))
    elif collaborators:
        recipients = [
            Recipient.from_user_id(collaborator['user_id'])
            for collaborator in collaborators
        ]
    else:
        # if there's no maintainer and there aren't any collaborators, use the creator
        recipients.append(Recipient.from_user_id(package['creator_user_id']))

    return recipients


def create_package_email(mail_dict: dict, package: dict):
    """
    Updates the given mail dict with the right details to contact the owner(s) of the
    given package.

    :param mail_dict: the mail dict to update
    :param package: the package dict
    """
    owners = get_package_owners(package)
    mail_dict['recipient_name'], mail_dict['recipient_email'] = zip(*owners)

    package_title = package['title'] or package['name']
    mail_dict['subject'] = f'Message regarding dataset: {package_title}'
    mail_dict['body'] += (
        '\n\nYou have been sent this enquiry via the data portal '
        f'as you are the author of dataset {package_title}.  Our apologies '
        'if this isn\'t relevant - please forward this onto '
        'data@nhm.ac.uk and we will respond.\nMany thanks, '
        'Data Portal team\n\n'
    )
