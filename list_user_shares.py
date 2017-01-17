#!/usr/bin/env python
#coding: utf-8

from seaserv import seafile_api, ccnet_api
import sys

def main():
    user = sys.argv[1]
    shared_repos = seafile_api.get_share_out_repo_list(user, -1, -1)
    for repo in shared_repos:
        if repo.is_virtual:
            print "Folder %s of Repo %s, shared to:" % (repo.origin_path, repo.origin_repo_id)
        else:
            print "Repo %s (%s), shared to:" % (repo.repo_id, repo.name)
        sgroups = seafile_api.list_repo_shared_group(user, repo.repo_id)
        print "groups:"
        for sgroup in sgroups:
            print "%s (%d)" % (ccnet_api.get_group(sgroup.group_id).group_name, sgroup.group_id)
        susers = seafile_api.list_repo_shared_to(user, repo.repo_id)
        print "users:"
        for suser in susers:
            print "%s" % suser.user


if __name__ == '__main__':
    main()
