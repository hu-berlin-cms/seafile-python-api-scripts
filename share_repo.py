#!/usr/bin/env python
#coding: utf-8

from seaserv import seafile_api, ccnet_api
import sys

def main():
# FIXME / TODO
## * use argparse
## * use fitting api request:
### share_repo or set_share_permission (if already exists)
## share_repo for already existing share returned 0 as well, but didn't work (6.1.4)
    repo_id = sys.argv[1]
    from_user = sys.argv[2]
    to_user = sys.argv[3]
    perm = sys.argv[4]
    ret = seafile_api.share_repo(repo_id, from_user, to_user, perm)
    print ret

if __name__ == '__main__':
    main()
