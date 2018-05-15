#!/usr/bin/env python
# coding: utf-8

from seaserv import seafile_api
import time
import pro

import os
import sys

os.environ.update(pro.get_seafes_env())

from seahub.utils import delegate_query_office_convert_status, gen_file_get_url, gen_inner_file_get_url, add_office_convert_task
import argparse

def main():
    cmd_parser = argparse.ArgumentParser(
        description="check document preview"
    )
    cmd_parser.add_argument("repo", help="repo/library uuid")
    cmd_parser.add_argument("file", help="file path")
    cmd_parser.add_argument("-t", '--type', dest="type", default='pdf', help="file type")
    cmd_parser.add_argument("-u", '--user', dest="user", default='admin', help="repo owner")
    cmd_parser.add_argument("-w", dest="warn_time", default="10", help="warning time in seconds", type=int)
    cmd_parser.add_argument("-c", dest="crit_time", default="30", help="critical time in seconds", type=int)
    cmd_parser.add_argument('-V', '--verbose', action="store_true",
                            dest="verbose",
                            help="Give detailed information, if possible")
    args = cmd_parser.parse_args()

    repo = seafile_api.get_repo(args.repo)
    file_id = seafile_api.get_file_id_by_path(repo.id, args.file)

    token = seafile_api.get_fileserver_access_token(repo.id,
                file_id, 'view', args.user, use_onetime=True)
    inner_url = gen_inner_file_get_url(token, os.path.basename(args.file))

    add_office_convert_task(file_id, args.type, inner_url, internal=True)

    start_time = time.time()

    while time.time() < start_time + args.crit_time:
        status = delegate_query_office_convert_status(file_id, 1)['status']
        if status == 'DONE':
            break
        time.sleep(1)

    end_time = time.time()

    if start_time + args.warn_time < end_time < start_time + args.crit_time:
        print 'WARN - %d seconds' % (end_time - start_time)
        sys.exit(1)
    elif end_time >= start_time + args.crit_time:
        print 'CRIT - %d seconds' % (end_time - start_time)
        sys.exit(2)
    else:
        print 'OK - %d seconds' % (end_time - start_time)


if __name__ == '__main__':
    main()
