#!/usr/bin/env python
# coding: utf-8

from seaserv import seafile_api
import argparse


def print_output_head(vals):
    print ",".join([x for x in vals.keys()])

def print_output(repo_id, vals):
    output_format = ",".join(["%%%s" % vals[x]['type'] for x in vals.keys()])
    output = output_format % tuple([vals[x]['val'] for x in vals.keys()])
    print "%s: %s" % (repo_id, output)

    # print "%s: %s,%s,%d" % (repo.id, repo.name, repo.desc, repo.version)


def main():
    cmd_parser = argparse.ArgumentParser(
        description="show infos"
    )
    cmd_parser.add_argument("repo", help="repo/library uuid", nargs='+')
    cmd_parser.add_argument('-o', '--owner', action="store_true",
                            dest="owner",
                            help="show repo owner")
    cmd_parser.add_argument('-V', '--verbose', action="store_true",
                            dest="verbose",
                            help="Give detailed information, if possible")
    args = cmd_parser.parse_args()

    invalid_repos = []

    first = True
    for repo_id in args.repo:
        repo = seafile_api.get_repo(repo_id)
        if repo:
            output = {'name': {'type': 's', 'val': repo.name},
                      'desc': {'type': 's', 'val': repo.desc},
                      'version': {'type': 'd', 'val': repo.version}}
            if args.owner:
                owner = seafile_api.get_repo_owner(repo_id)
                output['owner'] = {'type': 's', 'val': owner}

            if first:
                print_output_head(output)
                first = False

            print_output(repo_id, output)
        else:
            invalid_repos.append(repo_id)


if __name__ == '__main__':
    main()
