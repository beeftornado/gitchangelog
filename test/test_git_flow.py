#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Tests the option `git_flow` that is supposed to improve the changelog
knowing that the developers use the git flow style of branching.

http://nvie.com/posts/a-successful-git-branching-model/

Knowing the developers use certain terminology to tag the branch can help
gitchangelog parse the tree even better. gitchangelog defaults to including
merge commits because it assumes most people use a rebasing strategy. For
those teams that don't though, and instead use merging more often than rebasing,
they will most likely turn this option off so the changelog is not spammed with
merge commits. Hotfixes based on master will be merged back to master and also
to develop. Feature branches that are developed for a long time will frequently
merge develop into their feature branch. Once the feature is merged into the
repository's develop branch, the changelog will either be spammed with merges
if the option is on, or will include no mention of the final merge at all if
the option is off. Personally, I've been creating empty commits afer the merge
to create a changelog entry, but I strive for better!

If we know that in the typical git flow fashion, new feature branches start
with 'feature[-/]*' and fixes with 'fix[-/]*', then we should be able to
exclude all merge commits, except these special ones, denoting the completion
of something. These we *should* show, and even be able to drop in the right
category. That's the goal.

Use cases intended to be covered by this test:
- Initialize a git flow repo, test that turning off merge commits and git flow
options result in a changelog missing the facts that the features were
completed.
- If the merge commits are turned off and git flow turned on, a changelog
entry should appear for the completion of features and fixes.

Run test with: python -m unittest discover -fv -s test

"""

from __future__ import unicode_literals

import difflib

from common import GitChangelogTestCase, w


class TestGitFlowOption(GitChangelogTestCase):

    """ Test git flow use cases """

    def setUp(self):
        super(GitChangelogTestCase, self).setUp()

        with open('{0}/reference_changelogs/git_flow'.format(self.BASE)) as changelog:
            self.GITFLOW_REFERENCE = \
                changelog.read().decode('string-escape').decode("utf-8")

    def test_git_flow_repo_with_default_config_skips_features(self):
        """ Test without git flow option, no entries appear for new features """

        w("""
            cat <<EOF > .gitchangelog.rc

include_merges = False
git_flow = False

EOF
            ## Feature Branch
            git checkout -b feature/long_feature_1

            ## Hack on feature
            git commit -m 'new: started feature x' \
                --author 'Monty <monty@example.com>' \
                --date '2000-01-08 11:00:00' \
                --allow-empty

            git commit -m 'fix: something i broke in x' \
                --author 'Monty <monty@example.com>' \
                --date '2000-01-09 11:00:00' \
                --allow-empty

            ## Feature done, merge back, assume fast-forward wasn't possible
            git checkout master
            git merge --no-ff --commit feature/long_feature_1

        """)
        changelog = w('$tprog')

        ## The changelog should have no record of this newly added feature
        self.assert_not_contains(changelog, "feature x")
        self.assert_not_contains(changelog, "long_feature_1")
        self.assert_not_contains(changelog, "long feature 1")
        self.assertEqual(changelog, self.REFERENCE,
                         msg='Should match our reference output... diff from what it should be:\n%s' %
                             '\n'.join(
                             difflib.unified_diff(self.REFERENCE.split('\n'), changelog.split('\n'),
                                                  lineterm='')))

    def test_git_flow_repo_with_new_config_includes_feature(self):
        """ Test with git flow option, entries appear for new features """

        w("""
            cat <<EOF > .gitchangelog.rc

include_merges = False
git_flow = True

EOF
            ## Feature Branch
            git checkout -b feature/long_feature_1

            ## Hack on feature
            git commit -m 'new: started feature x' \
                --author 'Monty <monty@example.com>' \
                --date '2000-01-08 11:00:00' \
                --allow-empty

            git commit -m 'fix: something i broke in x' \
                --author 'Monty <monty@example.com>' \
                --date '2000-01-09 11:00:00' \
                --allow-empty

            ## Feature done, merge back, assume fast-forward wasn't possible
            git checkout master
            git merge --no-ff --commit feature/long_feature_1

        """)
        changelog = w('$tprog')

        ## The changelog should have a record of this newly added feature
        self.assert_contains(changelog, "long feature 1")
        self.assertEqual(changelog, self.GITFLOW_REFERENCE,
                         msg='Should match our reference output... diff from what it should be:\n%s' %
                             '\n'.join(
                             difflib.unified_diff(self.GITFLOW_REFERENCE.split('\n'), changelog.split('\n'),
                                                  lineterm='')))

    def test_git_flow_repo_with_new_config_includes_fix(self):
        """ Test with git flow option, entries appear for new fixes """

        w("""
            cat <<EOF > .gitchangelog.rc

include_merges = False
git_flow = True

EOF
            ## Hotfix Branch
            git checkout -b fix/long_fix_1

            ## Hack on fix
            git commit -m 'fix: bug x' \
                --author 'Monty <monty@example.com>' \
                --date '2000-01-08 11:00:00' \
                --allow-empty

            ## Fix done, merge back, assume fast-forward wasn't possible
            git checkout master
            git merge --no-ff --commit fix/long_fix_1

        """)
        changelog = w('$tprog')

        ## The changelog should have a record of this new fix
        self.assert_contains(changelog, "long fix 1")

    def test_git_flow_skips_normal_merges(self):
        """ Test the git flow option doesn't introduce merge commits other than features and bug fixes """

        w("""
            cat <<EOF > .gitchangelog.rc

include_merges = False
git_flow = True

EOF
            ## Feature Branch
            git checkout -b feature/long_feature_1

            ## Hack on feature
            git commit -m 'new: started feature x' --author 'Monty <monty@example.com>' \
                --date '2000-01-08 11:00:00' --allow-empty

            git commit -m 'fix: something i broke in x' --author 'Monty <monty@example.com>' \
                --date '2000-01-09 11:00:00' --allow-empty

            ## Progress made directly on the ancestor branch
            git checkout master
            git commit -m 'chg: i made lots of progress' --author 'Monty <monty@example.com>' \
                --date '2000-01-10 11:00:00' --allow-empty

            ## Merge that progress into the feature branch
            git checkout feature/long_feature_1
            git merge --no-ff --commit master

            ## Feature done, merge back, assume fast-forward wasn't possible
            git checkout master
            git merge --no-ff --commit feature/long_feature_1

            ## Fictional non-feature merge into master
            git commit -m 'Merge branch \'develop\' into master' --allow-empty

        """)
        changelog = w('$tprog')

        ## The changelog should have a record of this newly added feature
        self.assert_contains(changelog, "long feature 1")

        ## But it shouldn't show us the intermediary merge of master into feature
        self.assert_not_contains(changelog, "master")

    def test_git_flow_w_long_merge_text(self):
        """ Test the git flow option produces the correct message with either long or short merge text """

        ## Merges could show up as "Merge branch 'x' into y"
        ## or "Merge branch 'x'"

        w("""
            cat <<EOF > .gitchangelog.rc

include_merges = False
git_flow = True

EOF
            ## Instead of creating a real git history, I find it easier to fake the merges
            git commit -m 'Merge branch feature/big_feature into develop' --allow-empty
            git commit -m 'Merge branch fix/save_the_world' --allow-empty

        """)
        changelog = w('$tprog')

        ## The changelog should have properly formatted text for both
        self.assert_contains(changelog, "Completed big feature")
        self.assert_contains(changelog, "Fixed save the world")
        self.assert_not_contains(changelog, "into develop")

    def test_git_flow_hotfix_branch(self):
        """ Test the git flow option counts hotfixes as fixes """

        w("""
            cat <<EOF > .gitchangelog.rc

include_merges = False
git_flow = True

EOF
            ## Instead of creating a real git history, I find it easier to fake the merges
            git commit -m 'Merge branch hotfix/ticket-123_red_button into develop' --allow-empty

        """)
        changelog = w('$tprog')

        ## The changelog should have properly formatted text for both
        self.assert_contains(changelog, "Fixed ticket-123 red button")
        self.assert_not_contains(changelog, "into develop")
