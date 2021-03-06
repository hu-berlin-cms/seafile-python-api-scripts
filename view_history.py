#!/usr/bin/env python
# coding: utf-8

from seaserv import seafile_api
from seafobj.commits import commit_mgr
from seafobj import fs_mgr
from seafobj.commit_differ import CommitDiffer
from collections import deque
import datetime
import argparse
import sys

traversed_commits = set()


def get_blocks(repo_id, version, root):
    queued_dirs = [root]
    blocks = set()
    while queued_dirs:
        cdir = fs_mgr.load_seafdir(repo_id, version, queued_dirs.pop())
        for dent in cdir.get_files_list():
            seafFile = fs_mgr.load_seafile(repo_id, version, dent.id)
            blocks.update(seafFile.blocks)

        for dent in cdir.get_subdirs_list():
            queued_dirs.append(dent.id)

    return blocks


def block_diff(repo_id, version, root1, root2):
    if root1 == root2:
        return ([], [])

    blocks1 = get_blocks(repo_id, version, root1)
    blocks2 = get_blocks(repo_id, version, root2)
    return (list(blocks2.difference(blocks1)),
            list(blocks1.difference(blocks2)))


def print_history_blocks(commit):
    out = {
        'added': [],
        'deleted': [],
           }

    if commit.parent_id:
        parent = commit_mgr.load_commit(commit.repo_id, commit.version, commit.parent_id)  # noqa
        (out['added'], out['deleted']) = block_diff(
            commit.repo_id, commit.version, parent.root_id, commit.root_id)

        print "commit %s" % commit.commit_id
        print "Author: %s" % commit.creator_name
        print "Date: %s" % datetime.datetime.utcfromtimestamp(
            commit.ctime).strftime('%Y-%m-%d %H:%M:%SZ')
        if commit.second_parent_id:
            print "Merge Commit"
        print ""
        for key in out.keys():
            print "%s:" % key
            for val in out[key]:
                print val

        print ""


def print_history(commit):
    out = {
        'added_files': [],
        'deleted_files': [],
        'added_dirs': [],
        'deleted_dirs': [],
        'modified_files': [],
        'renamed_files': [],
        'moved_files': [],
        'renamed_dirs': [],
        'moved_dirs': []
           }

    if commit.parent_id:
        parent = commit_mgr.load_commit(commit.repo_id, commit.version, commit.parent_id)  # noqa
        differ = CommitDiffer(commit.repo_id, commit.version,
                              parent.root_id, commit.root_id)
        (out['added_files'], out['deleted_files'], out['added_dirs'],
         out['deleted_dirs'], out['modified_files'], out['renamed_files'],
         out['moved_files'], out['renamed_dirs'],
         out['moved_dirs']) = differ.diff()

        print "commit %s" % commit.commit_id
        print "Author: %s" % commit.creator_name
        print "Date: %s" % datetime.datetime.utcfromtimestamp(
            commit.ctime).strftime('%Y-%m-%d %H:%M:%SZ')
        if commit.second_parent_id:
            print "Merge Commit"
        print ""
        for key in out.keys():
            print "%s:" % key
            for val in out[key]:
                print val.path

        print ""


def print_commit_edge_list(commit):
    if commit.parent_id:
        print "%.8s,%.8s" % (commit.commit_id, commit.parent_id)
    if commit.second_parent_id:
        print "%.8s,%.8s" % (commit.commit_id, commit.second_parent_id)


def traverse_commits(commit_mgr, func, repo_id, repo_version, commit_id,
                     only_parent=False):
    to_traverse = deque([commit_id])

    # iterate over commits
    while to_traverse:
        commit_id = to_traverse.popleft()
        # don't traverse commits twice
        traversed_commits.add(commit_id)
        commit = commit_mgr.load_commit(repo_id, repo_version, commit_id)

        # do work
        func(commit)

        if commit.parent_id:
            if commit.parent_id not in traversed_commits:
                to_traverse.append(commit.parent_id)

        if commit.second_parent_id and not only_parent:
            if commit.second_parent_id not in traversed_commits:
                to_traverse.append(commit.second_parent_id)


def main():
    cmd_parser = argparse.ArgumentParser(
        description="show repo history"
    )
    cmd_parser.add_argument("repo", help="repo/library uuid")
    cmd_parser.add_argument('-t', '--tree', action="store_true",
                            dest="tree",
                            help="output history edge list for drawing tree")
    cmd_parser.add_argument('-b', '--blocks', action="store_true",
                            dest="blocks",
                            help="Show block changes in history")
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
    elif args.blocks:
        traverse_commits(commit_mgr, print_history_blocks, repo.id,
                         repo.version, repo.head_cmmt_id, only_parent=True)
    else:
        traverse_commits(commit_mgr, print_history, repo.id,
                         repo.version, repo.head_cmmt_id, only_parent=True)


if __name__ == '__main__':
    main()
