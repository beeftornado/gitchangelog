# -*- encoding: utf-8 -*-

"""
Tests the option `replace_unreleased_version_label` that is supposed to replace
the unreleased version string with a git generated version description.

Use cases intended to be covered by this test:
- Option is off, output should be unchanged from default.
- Option is on, but last commit is tagged, output should be unchanged.
- Option is on, and there have been additional commits, output should lead with git version string.

Run test with: python -m unittest discover -fv -s test

"""

from __future__ import unicode_literals

import difflib

from common import GitChangelogTestCase, w


class TestGitVersionStringOption(GitChangelogTestCase):
    """ Test that unreleased versions use the right option """

    def test_default_case(self):
        """ Test if the option is off then the log uses default behavior """

        REFERENCE_CHANGELOG = r"""Changelog
=========

%%version%% (unreleased)
------------------------

Changes
~~~~~~~

- Modified ``b`` XXX. [Alice]

Fix
~~~

- Something. [Alice]

0.0.3 (2000-01-05)
------------------

New
~~~

- Add file ``e``, modified ``b`` [Bob]

- Add file ``c`` [Charly]

0.0.2 (2000-01-02)
------------------

New
~~~

- Add ``b`` with non-ascii chars éèàâ§µ. [Alice]


"""

        w("""

            cat <<EOF > .gitchangelog.rc

replace_unreleased_version_label = False

EOF
            ## Branch
            git checkout master
            git checkout -b test_default_case

            ## Build the tree
            git commit -m 'fix: something' \
                --author 'Alice <alice@example.com>' \
                --date '2000-01-07 11:00:00' \
                --allow-empty

        """)
        changelog = w('$tprog')
        self.assertEqual(
            changelog, REFERENCE_CHANGELOG,
            msg="Should match our reference output... "
            "diff from what it should be:\n%s"
            % '\n'.join(difflib.unified_diff(REFERENCE_CHANGELOG.split("\n"),
                                             changelog.split("\n"),
                                             lineterm="")))

    def test_version_tagged(self):
        """ Test if the option is on and the last commit is tagged, then the log uses the tag """

        REFERENCE_CHANGELOG = r"""Changelog
=========

0.0.4 (2000-01-07)
------------------

Changes
~~~~~~~

- Modified ``b`` XXX. [Alice]

Fix
~~~

- Something. [Alice]

0.0.3 (2000-01-05)
------------------

New
~~~

- Add file ``e``, modified ``b`` [Bob]

- Add file ``c`` [Charly]

0.0.2 (2000-01-02)
------------------

New
~~~

- Add ``b`` with non-ascii chars éèàâ§µ. [Alice]


"""

        w("""

            cat <<EOF > .gitchangelog.rc

replace_unreleased_version_label = True

EOF
            ## Branch
            git checkout master
            git checkout -b test_default_case

            ## Build the tree
            git commit -m 'fix: something' \
                --author 'Alice <alice@example.com>' \
                --date '2000-01-07 11:00:00' \
                --allow-empty

            git tag 0.0.4

        """)
        changelog = w('$tprog')
        self.assertEqual(
            changelog, REFERENCE_CHANGELOG,
            msg="Should match our reference output... "
            "diff from what it should be:\n%s"
            % '\n'.join(difflib.unified_diff(REFERENCE_CHANGELOG.split("\n"),
                                             changelog.split("\n"),
                                             lineterm="")))

    def test_unreleased_version(self):
        """ Test if the option is on and the last commit is not tagged, then the log uses the generated version """

        REFERENCE_CHANGELOG = r"""Changelog
=========

0.0.3-2.dev_r200001071900
-------------------------

Changes
~~~~~~~

- Modified ``b`` XXX. [Alice]

Fix
~~~

- Something. [Alice]

0.0.3 (2000-01-05)
------------------

New
~~~

- Add file ``e``, modified ``b`` [Bob]

- Add file ``c`` [Charly]

0.0.2 (2000-01-02)
------------------

New
~~~

- Add ``b`` with non-ascii chars éèàâ§µ. [Alice]


"""

        w("""

            cat <<EOF > .gitchangelog.rc

replace_unreleased_version_label = True

EOF
            ## Branch
            git checkout master
            git checkout -b test_default_case

            ## Build the tree
            git commit -m 'fix: something' \
                --author 'Alice <alice@example.com>' \
                --date '2000-01-07 11:00:00' \
                --allow-empty

        """)
        changelog = w('$tprog')
        self.assertEqual(
            changelog, REFERENCE_CHANGELOG,
            msg="Should match our reference output... "
            "diff from what it should be:\n%s"
            % '\n'.join(difflib.unified_diff(REFERENCE_CHANGELOG.split("\n"),
                                             changelog.split("\n"),
                                             lineterm="")))

    def test_unreleased_version_nonstandard_tags(self):
        """ Test git version string works if tag format isn't semantic.

        Test if the option is on and the last commit is not tagged,
        and the tag format is not the standard semantic version, then it still works.

        eg. tags like 'sprint-x' with commits after the tag, should output
        'sprint-x-y', with y being the number of commits post tag. Previous code
        would mangle it into just 'sprint-x' """

        REFERENCE_CHANGELOG = r"""Changelog
=========

sprint-8-1.dev_r200001071900
----------------------------

Fix
~~~

- Something. [Alice]

sprint-8 (2000-01-06)
---------------------

Changes
~~~~~~~

- Modified ``b`` XXX. [Alice]

0.0.3 (2000-01-05)
------------------

New
~~~

- Add file ``e``, modified ``b`` [Bob]

- Add file ``c`` [Charly]

0.0.2 (2000-01-02)
------------------

New
~~~

- Add ``b`` with non-ascii chars éèàâ§µ. [Alice]


"""

        w("""

            cat <<EOF > .gitchangelog.rc

tag_filter_regexp = r'^sprint[\-\.\s\_]*\d+|[0-9]+(?:\.[0-9]+(\.[0-9]+)?)?$'
replace_unreleased_version_label = True

EOF
            ## Branch
            git checkout master

            git tag sprint-8

            git checkout -b test_default_case

            ## Build the tree
            git commit -m 'fix: something' \
                --author 'Alice <alice@example.com>' \
                --date '2000-01-07 11:00:00' \
                --allow-empty

        """)
        changelog = w('$tprog')
        self.assertEqual(
            changelog, REFERENCE_CHANGELOG,
            msg="Should match our reference output... "
            "diff from what it should be:\n%s"
            % '\n'.join(difflib.unified_diff(REFERENCE_CHANGELOG.split("\n"),
                                             changelog.split("\n"),
                                             lineterm="")))
