#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

from seaserv import seafile_api, ccnet_api
import argparse


def main():
    cmd_parser = argparse.ArgumentParser(
        description="get user info"
    )
    cmd_parser.add_argument('user', help="user we are interested in")
    cmd_parser.add_argument('-s', '--shares', action="store_true",
                            dest="shares", help="show shares of a user")
    cmd_parser.add_argument(
        '-b', '--base-dn',
        default="ou=users,ou=Benutzerverwaltung,"
                "ou=Computer- und Medienservice,"
                "o=Humboldt-Universitaet zu Berlin,c=DE",
        dest="base_dn", help="base dn for search")
    cmd_parser.add_argument('-V', '--verbose', action="store_true",
                            dest="verbose",
                            help="Give detailed information, if possible")
    args = cmd_parser.parse_args()

    if args.shares:
        show_share_info(args.user)


def show_share_info(user):
    shared_repos = seafile_api.get_share_out_repo_list(user, -1, -1)
    shared_repos += seafile_api.get_group_repos_by_owner(user)

    for repo in shared_repos:
        if repo.is_virtual:
            print("Folder %s of Repo %s, shared to:" % (repo.origin_path, repo.origin_repo_id))
        else:
            print("Repo %s (%s), shared to:" % (repo.repo_id, repo.name))
        sgroups = seafile_api.list_repo_shared_group(user, repo.repo_id)
        print("groups:")
        for sgroup in sgroups:
            print("%s (%d)" % (ccnet_api.get_group(sgroup.group_id).group_name, sgroup.group_id))
        susers = seafile_api.list_repo_shared_to(user, repo.repo_id)
        print("users:")
        for suser in susers:
            print("%s" % suser.user)


if __name__ == '__main__':
    main()
