#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

import django
django.setup()  # noqa

from seaserv import seafile_api, ccnet_api
from seahub.base.models import UserLastLogin
from seahub.api2.models import Token, TokenV2, DESKTOP_PLATFORMS
from seahub.utils.timeutils import datetime_to_isoformat_timestr
import argparse


def main():
    cmd_parser = argparse.ArgumentParser(
        description="get user info"
    )
    cmd_parser.add_argument('user', help="user we are interested in")
    cmd_parser.add_argument('-l', '--login-details', action="store_true",
                            dest="login",
                            help="show user login info")
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

    if args.login:
        show_login_details(args.user)


def show_share_info(user):
    shared_repos = seafile_api.get_share_out_repo_list(user, -1, -1)
    shared_repos += seafile_api.get_group_repos_by_owner(user)

    shown_repos = set()

    for repo in shared_repos:
        if repo.repo_id in shown_repos:
            continue

        shown_repos.add(repo.repo_id)

        if repo.is_virtual:
            print("Folder %s of Repo %s, shared to:" % (repo.origin_path, repo.origin_repo_id))
        else:
            print("Repo %s (%s), shared to:" % (repo.repo_id, repo.name))
        sgroups = seafile_api.list_repo_shared_group(user, repo.repo_id)
        print("groups:")
        for sgroup in sgroups:
            print("%s (%d), %s" % (ccnet_api.get_group(sgroup.group_id).group_name, sgroup.group_id, sgroup.perm))
        susers = seafile_api.list_repo_shared_to(user, repo.repo_id)
        print("users:")
        for suser in susers:
            print("%s, %s" % (suser.user, suser.perm))


def show_login_details(user):
    # print(seafile_api.list_repo_tokens_by_email(user))
    # print(ccnet_api.get_emailuser(user).__dict__)
    # ctime, is_staff, is_active, id
    print("active: %s" % ccnet_api.get_emailuser(user).is_active)
    print("last login: %s" % _get_last_login(user))
    v1token = _get_v1token(user)
    if v1token is not None:
        print("v1 token created at: %s" % v1token.created)
    else:
        print("no v1 token")
    print("\ndevices:")

    out_table = [['device name', 'last accessed', 'platform', 'client version', 'desktop client', 'last login ip', 'device id']]
    for dev in _get_devices(user):
        out_table.append([dev['device_name'], dev['last_accessed'], "%s%s" % (dev['platform'], " (%s)" % dev['platform_version'] if dev['platform_version'] else ''), dev['client_version'], dev['is_desktop_client'], dev['last_login_ip'], dev['device_id']])

    _print_table(out_table)


def _get_v1token(user):
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        return None
    else:
        return token


def _get_last_login(user):
    last_login = UserLastLogin.objects.get(username=user)

    return last_login.last_login


def _get_devices(user):
    devices = TokenV2.objects.get_user_devices(user)

    for device in devices:
        device['last_accessed'] = datetime_to_isoformat_timestr(device['last_accessed'])
        device['is_desktop_client'] = False
        # don't want to see the key
        del device['key']
        if device['platform'] in DESKTOP_PLATFORMS:
            device['is_desktop_client'] = True

    return devices

# source: https://stackoverflow.com/a/19125514/1381638
def _print_table(tbl, borderHorizontal = '-', borderVertical = '|', borderCross = '+'):
    cols = [list(x) for x in zip(*tbl)]
    lengths = [max(map(len, map(str, col))) for col in cols]
    f = borderVertical + borderVertical.join(' {:>%d} ' % l for l in lengths) + borderVertical
    s = borderCross + borderCross.join(borderHorizontal * (l+2) for l in lengths) + borderCross

    print(s)
    for row in tbl:
        print(f.format(*row))
        print(s)


if __name__ == '__main__':
    main()
