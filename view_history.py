#!/usr/bin/env python
# coding: utf-8

from seaserv import seafile_api
from seafobj.commits import commit_mgr
import argparse
import sys

traversed_commits = set()


def print_commit_edge_list(commit):
    if commit.parent_id:
        print "%.8s,%.8s" % (commit.commit_id, commit.parent_id)
    if commit.second_parent_id:
        print "%.8s,%.8s" % (commit.commit_id, commit.second_parent_id)


def traverse_commits(commit_mgr, func, repo_id, repo_version, commit_id,
                     **kwargs):
    traversed_commits.add(commit_id)
    commit = commit_mgr.load_commit(repo_id, repo_version, commit_id)  # noqa
    func(commit)
    if commit.parent_id:
        if commit.parent_id not in traversed_commits:
            traverse_commits(commit_mgr, func, repo_id, repo_version,
                             commit.parent_id, **kwargs)
    if commit.second_parent_id and ('only_parent' not in kwargs or
                                    not kwargs['only_parent']):
        if commit.second_parent_id not in traversed_commits:
            traverse_commits(commit_mgr, func, repo_id, repo_version,
                             commit.second_parent_id, **kwargs)


def main():
    cmd_parser = argparse.ArgumentParser(
        description="show repo history"
    )
    cmd_parser.add_argument("repo", help="repo/library uuid")
    cmd_parser.add_argument('-t', '--tree', action="store_true",
                            dest="tree",
                            help="output history edge list for drawing tree")
    cmd_parser.add_argument('-V', '--verbose', action="store_true",
                            dest="verbose",
                            help="Give detailed information, if possible")
    args = cmd_parser.parse_args()

    repo = seafile_api.get_repo(args.repo)
    if not repo:
        sys.exit(-1)

    if args.tree:
        print "edge list:"
        traverse_commits(commit_mgr, print_commit_edge_list, repo.id,
                         repo.version, repo.head_cmmt_id)


if __name__ == '__main__':
    main()
