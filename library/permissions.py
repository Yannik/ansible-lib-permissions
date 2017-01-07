#!/usr/bin/env python
'''
    timedatectl ansible module

    This module supports setting ntp enabled
'''

EXAMPLES = '''
# 
- permissions:
    permissions:
      - { path: '/var/www/', recurse: yes, type: dirs, mode: 750 }
      - { path: '/var/www/avantfax', recurse: yes, type: dirs, mode: 700 }
'''

import os
from itertools import repeat

from ansible.module_utils.basic import AnsibleModule


def has_more_specific_permission(permissions, current_permission, path):
    global output
    for permission in permissions:
        if permission['path'] == current_permission['path']:
            continue

        # exact file permission given
        if path == permission['path'] and not permission['recurse']:
            return True

        # ignore less-specific permissions
        # for example, permission '/var/www/' for current_permission '/var/www/mysite/'
        if current_permission['path'].startswith(os.path.join(permission['path'], '')):
            continue

        # more specific directory permission given
        # for example, permission '/var/www/mysite/secret' for path '/var/www/mysite/secret/file'
        if path.startswith(os.path.join(permission['path'], '')):
            return True

    return False

def recursive_set_permission(module, permissions, current_permission, current_path):
    global output, indent
    changed = False
    for file in os.listdir(current_path):
        file = os.path.join(current_path, file)
        tmp_file_args = current_permission.copy()
        tmp_file_args['path'] = file
        output += indent + "Checking perms for " + file + "\n"
        if current_permission['path'] == '/home/yannik/dir/secret':
            pydevd.settrace('localhost', port=54655, stdoutToServer=True, stderrToServer=True)
        if not has_more_specific_permission(permissions, current_permission, file):
            output += indent + "Setting perms for " + file + "\n"
            changed |= module.set_fs_attributes_if_different(tmp_file_args, changed)
        if os.path.isdir(file):
            output += indent + "Starting new iteration for " + file + "\n"
            indent += "  "
            changed |= recursive_set_permission(module, permissions, current_permission, file)
            indent = indent[2:]
    return changed


def permission_with_file_common_arguments(permission, module):
    recurse = permission.get('recurse', False)
    permission = module.load_file_common_arguments(permission)
    permission['recurse'] = recurse
    return permission


def append_basepath_to_permission_path(permission, basepath):
    permission['path'] = os.path.join(basepath, permission['path'])
    return permission

output = ""
indent = ""

import pydevd

def main():
    global output
    ''' Ansible module for timedatectl
    '''

    module = AnsibleModule(
        argument_spec=dict(
            basepath=dict(type='path', required=False, default='/'),
            permissions=dict(type='list')
        ),
        supports_check_mode=True
    )

    params = module.params
    basepath = params['basepath']
    permissions = params['permissions']

    basepath = '/home/yannik'
    permissions = [
        {'path': 'dir', 'recurse': True, 'mode': '0750'},
        {'path': 'dir/secret', 'recurse': True, 'mode': '0700'},
        {'path': 'dir/secret', 'mode': '0755'}
    ]

    permissions = map(permission_with_file_common_arguments, permissions, repeat(module, len(permissions)))
    permissions = map(append_basepath_to_permission_path, permissions, repeat(basepath, len(permissions)))

    changed = False
    for permission in permissions:
        output += "\n" + "Working on permission" + permission['path'] + "\n"
        if not has_more_specific_permission(permissions, permission, permission['path']):
            output += indent + "[1]Setting perms for " + permission['path'] + "\n"
            changed |= module.set_fs_attributes_if_different(permission, changed)
        if os.path.isdir(permission['path']) and permission['recurse']:
            changed |= recursive_set_permission(module, permissions, permission, permission['path'])

    module.exit_json(changed=changed, output=output)

if __name__ == '__main__':
    main()
