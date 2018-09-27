#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

import django
django.setup()  # noqa

from seaserv import seafile_api, ccnet_api
from pysearpc import SearpcError
from seahub.base.models import UserLastLogin
from seahub.api2.models import Token, TokenV2, DESKTOP_PLATFORMS
from seahub.utils.timeutils import datetime_to_isoformat_timestr
import argparse


def main():
    cmd_parser = argparse.ArgumentParser(
        description="manage groups"
    )
    cmd_parser.add_argument('group_id', type=int, help="group we are interested in")
    cmd_parser.add_argument('-l', '--list', action="store_true",
                            dest="list_members",
                            help="show group members")
    cmd_parser.add_argument('-a', '--add-member', nargs='*',
                            dest="add_members", help="add users to group")
    cmd_parser.add_argument('-d', '--delete-member', nargs='*',
                            dest="delete_members", help="delete users from group")
    cmd_parser.add_argument('-V', '--verbose', action="store_true",
                            dest="verbose",
                            help="Give detailed information, if possible")
    args = cmd_parser.parse_args()

    if args.list_members:
        show_members(args.group_id)
    elif args.add_members:
        add_members(args.group_id, args.add_members)
    elif args.delete_members:
        delete_members(args.group_id, args.delete_members)


def show_members(group_id):
    print("group %s (%d):" % (ccnet_api.get_group(group_id).group_name, group_id))
    gusers = ccnet_api.get_group_members(group_id)
    for guser in gusers:
        print("%s" % (guser.user_name))
    print("")


def add_members(group_id, members):
    group = ccnet_api.get_group(group_id)
    print("Adding users to group %s (%d):" % (group.group_name, group_id))

    # WARNING: no check, if user exists!
    for member in members:
        try:
            ccnet_api.group_add_member(group_id, group.creator_name, member)
        except SearpcError:
            print("Error adding %s" % member)
        else:
            print("Added %s" % member)

    print("")


def delete_members(group_id, members):
    group = ccnet_api.get_group(group_id)
    print("Removing users from group %s (%d):" % (group.group_name, group_id))

    for member in members:
        try:
            ccnet_api.group_remove_member(group_id, group.creator_name, member)
        except SearpcError:
            print("Error removing %s" % member)
        else:
            print("Removed %s" % member)

    print("")


if __name__ == '__main__':
    main()
