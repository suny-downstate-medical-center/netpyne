
# How to contribute

Thank you for your interest in contributing to NetPyNE project!. NetPyNE is open source and available at [GitHub repository](https://github.com/Neurosim-lab/netpyne).

[NetPyNE](http://netpyne.org/overview.html) is currently being developed and supported by [Neurosin lab](http://neurosimlab.org/) and accepts contributions in the form of bug reports, fixes, feature additions, and documentation improvements (even just typo corrections). The best way to start contributing is by [opening an issue](https://github.com/Neurosim-lab/netpyne/issues) or [fork](https://help.github.com/en/articles/fork-a-repo) the repository on our GitHub page and make a [Pull Request](https://help.github.com/en/articles/creating-a-pull-request) with your changes.

Users and contributors to NetPyNE are expected to follow our [coding conventions](#coding-conventions).

#### Table Of Contents

- [Overview of contribution process](#overview-of-contribution-process)
- [Getting started](#getting-started)
  - [Configuring git](#configuring-git)
  - [Make a local copy of GitHub repository](#make-a-local-copy-of-github-repository)
  - [Basic git commands](#basic-git-commands)
  - [Connecting to GitHub with SSH (optional)](#connecting-to-github-with-ssh-optional)
- [Opening an issue](#opening-an-issue)
- [Opening a pull request](#opening-a-pull-request)
- [Coding conventions](#coding-conventions)

## Overview of contribution process
> _Hint:_ **Working on your first pull request?** Learn how from this guide in GitHub. [How to Contribute to Open Source Project](https://opensource.guide/how-to-contribute/)

In general you’ll be working with three different copies of the Neurosim-lab/netpyne repository codebase: the official remote copy at https://github.com/Neurosim-lab/netpyne (usually called upstream), your remote [fork](https://help.github.com/en/articles/fork-a-repo) of the upstream repository (similar URL, but with your username in place of Nuerosim-lab, and usually called origin), and the local copy of the codebase on your computer. The typical contribution process is to:

1. synchronize your local copy with `upstream`
2. make changes to your local copy
3. [push](https://help.github.com/en/articles/pushing-commits-to-a-remote-repository) your changes to `origin` (your remote fork of the `upstream`)
4. submit a [pull request](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) from your fork into `upstream`

The next sections describe this process in more detail.

## Getting started
> **Note:** If you are new in GitHubs see this [link](https://guides.github.com/activities/hello-world/).

### Configuring git
To get set up for contributing, make sure you have git installed on your local computer:

* On Linux, the command `sudo apt install git` is usually sufficient; see the [official Linux instructions](https://git-scm.com/download/linux) for more options.

* On MacOS, download the [.dmg installer](https://git-scm.com/download/mac); Atlassian also provides [more detailed instructions and alternatives](https://www.atlassian.com/git/tutorials/install-git) such as using MacPorts or Homebrew.

* On Windows, we recommend [git Bash](https://gitforwindows.org/) rather than the [official Windows version of git](https://git-scm.com/download/win), because git Bash provides its own shell that includes many Linux-equivalent command line programs that are useful for development. Windows 10 also offers the [Windows subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/about) that offers similar functionality to git Bash.

> **Git GUI alternative**
> [GitHub desktop](https://desktop.github.com/) is a GUI alternative to command line git that some users appreciate; it is available for :+1: Windowns and MacOS

Once git is installed, the only absolutely necessary configuration step is identifying yourself and your contact info:

```bash
~$ git config --global user.name "Your Name"
~$ git config --global user.email you@yourdomain.example.com
```

Make sure that the same email address is associated with your GitHub account and with your local git configuration. It is possible to associate multiple emails with a GitHub account, so if you initially set them up with different emails, just add the local email to the GitHub account.

To customize git’s behavior see [configuring git](https://www.git-scm.com/book/en/v2/Customizing-Git-Git-Configuration) for more information. Once you have git installed and configured, go to [the Neurosym-lab/netpyne GitHub page](https://github.com/Neurosim-lab/netpyne) and create a [fork](https://help.github.com/en/articles/fork-a-repo) into your GitHub user account.

### Make a local copy of GitHub repository

> **Supported Python environments**
>We strongly recommend the [Anaconda](https://www.anaconda.com/distribution/) or [Miniconda](https://conda.io/en/latest/miniconda.html) environment managers for Python.

You must clone the Nerosim-lab/netpyne repository from your remote fork, and also connect the local copy to the `upstream` version of the codebase, so you can stay up-to-date with changes from other contributors.

Make a local clone of your remote fork (`origin`):

```bash
 ~$ cd $INSTALL_LOCATION
 ~$ git clone https://github.com/$GITHUB_USERNAME/netpyne.git
```

> **Remote URLs in git**
>Here we use `git://` instead of `https://` in the URL for the `upstream` remote repository. `git://` URLs are read-only, so you can `pull` changes from `upstream` into your local copy (to stay up-to-date with changes from other contributors) but you cannot `push` changes from your computer into the `upstream` remote. Instead, you must `push` your changes to your own remote fork (`origin`) first, and then create a pull request from your remote into the `upstream` remote. In [a later section](#connecting-to-github-with-ssh-optional) you’ll see a third kind of remote URL for connecting to GitHub using SSH.

Finally, set up a link between your local clone and the official repository (`upstream`):

```bash
~$ cd netpyne
~$ git remote add upstream https://github.com/Neurosim-lab/netpyne.git
~$ git fetch --all
~$ git remote -v   #Shows your tracked repositories.
```

### Basic git commands

Learning to work with git can take a long time, because it is a complex and powerful tool for managing versions of files across multiple users, each of whom have multiple copies of the codebase. We’ve already seen in the setup commands above a few useful git commands:

* `git clone <URL_OF_REMOTE_REPO>` (make a local copy of a repository).
* `git remote add <NICKNAME_OF_REMOTE> <URL_OF_REMOTE_REPO>` (connect a local copy to an additional remote).
* `git fetch --all` (get the current state of connected remote repos).

Other commands that you will undoubtedly need related to branches can be found [here](https://help.github.com/en/articles/about-branches). Branches represent multiple copies of the codebase within a local clone or remote repo. Branches are typically used to experiment with new features while still keeping a clean, working copy of the original codebase that you can switch back to at any time. The default branch of any repo is always called `master`, and it is recommended that you reserve the `master` branch to be that clean copy of the working `upstream` codebase. 

In Neurosim-lab/netpyne repo, you must not work in the `master` branch, there is a branch called `development` for contribuiting. Therefore, if you want to add a new change, you should first synchronize your local `development` branch with the `upstream` repository, then create a new branch based on `development` and [check it out](https://git-scm.com/docs/git-checkout) so that any changes you make will exist on that new branch:

```bash
 ~$ git checkout development            # switch to local development branch
 ~$ git fetch upstream                  # get the current state of the remote upstream repo
 ~$ git merge upstream/development      # synchronize local development branch with remote upstream development branch
 ~$ git checkout -b new-branch          # create local branch "new-branch" and check it out
```

> **Alternative**
> You can save some typing by using `~$ git pull upstream/development` to replace the `fetch` and `merge` lines above.

> **Note:** You could synchronize your local `master` branch with the `upstream` repository to have the update version, but you **_must not_** work in any change on the `master` branch.

Now that you’re on a new branch, you can fix a bug or add a new feature, add a test, update the documentation, etc. When you’re done, it’s time to organize your changes into a series of [commits](https://git-scm.com/docs/git-commit). Commits are like snapshots of the repository — actually, more like a description of what has to change to get from the most recent snapshot to the current snapshot.

Git knows that people often work on multiple changes in multiple files all at once, but that ultimately they should separate those changes into sets of related changes that are grouped together based on common goals (so that it’s easier for their colleagues to understand and review the changes). For example, you might want to group all the code changes together in one commit, put new unit tests in another commit, and changes to the documentation in a third commit. Git makes this easy(ish) with something called the [stage](https://git-scm.com/book/en/v2/Git-Tools-Interactive-Staging) (or _staging area_). After you’ve made some changes to the codebase, you’ll have what git calls “unstaged changes”, which will show up with the [status](https://git-scm.com/docs/git-status) command:

```bash
 ~$ git status    # see what state the local copy of the codebase is in
```

Those unstaged changes can be [added](https://git-scm.com/docs/git-add) to the stage one by one, by either adding a whole file’s worth of changes, or by adding only certain lines interactively:

```bash
 ~$ git add some_file.py               # add all the changes you made to this file
 ~$ git add some_new_file.py           # add a completely new file in its entirety
 ~$ git add -p docs/some_other_file.py # enter interactive staging mode, to add only portions of a file.
```

Once you’ve collected all the related changes together on the stage, the `git status` command will now refer to them as _“changes staged for commit”_. You can commit them to the current branch with the [commit](https://git-scm.com/docs/git-commit) command. If you just type `git commit` by itself, git will open the text editor you configured it to use so that you can write a _commit message_ — a short description of the changes you’ve grouped together in this commit. You can bypass the text editor by passing a commit message on the command line with the `-m` flag. For example, if your first commit adds a new feature, your commit message might be:

```bash
 ~$ git commit -m 'Author: adds feature X'
```

Once you’ve made the commit, the stage is now empty, and you can repeat the cycle. When you’re done and everything looks good, it’s time to push your changes to your fork:

```bash
 # push local changes to remote branch origin/new-branch
 # (this will create the remote branch if it doesn't already exist)
 ~$ git push origin your-branch
```

Finally, go to the [Neurosin-lab/netpyne GitHub page](https://github.com/Neurosim-lab/netpyne), click on the pull requests tab, click the “new pull request” button, and choose “compare across forks” to select `your-branch` as the “head repository” and select `development` branch as "base repository".

> **Note:** See the GitHub help page on [creating a PR from a fork](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork) for more information about opening pull requests. To learn more about git, check out the [GitHub help website](https://help.github.com/en), the [GitHub Learning Lab](https://lab.github.com/) tutorial series, and the [pro git book](https://git-scm.com/book/en/v2).

### Connecting to GitHub with SSH (optional)

One easy way to speed up development is to reduce the number of times you have to type your password. SSH (secure shell) allows authentication with pre-shared key pairs. The private half of your key pair is kept secret on your computer, while the public half of your key pair is added to your GitHub account; when you connect to GitHub from your computer, the local git client checks the remote (public) key against your local (private) key, and grants access your account only if the keys fit. GitHub has several help pages that guide you through the process.

Once you have set up GitHub to use SSH authentication, you should change the addresses of your Netpyne-lab GitHub remotes, from `https://` addresses to `git@` addresses, so that git knows to connect via SSH instead of HTTPS.
>**Note:** You only could have a _SSH key_ from a repository you are a contributor.

## Opening an issue

You should usually open an issue in the following situations:

* Report an error you can’t solve yourself.
* Discuss a high-level topic or idea (for example, community, vision or policies)
* Propose a new feature or other project idea

Tips for communicating on issues:

* **If you see an open issue that you want to tackle**, comment on the issue to let people know you’re on it. That way, people are less likely to duplicate your work.
* **If an issue was opened a while ago**, it’s possible that it’s being addressed somewhere else, or has already been resolved, so comment to ask for confirmation before starting work.
* **If you opened an issue, but figured out the answer later on your own**, comment on the issue to let people know, then close the issue. Even documenting that outcome is a contribution to the project.

> **Note:** See in [GitHub Help](https://help.github.com/en) how to [creating an issue](https://help.github.com/en/articles/creating-an-issue).

## Opening a pull request

You should usually open a pull request in the following situations:

* Submit trivial fixes (for example, a typo, a broken link or an obvious error).
* Start work on a contribution that was already asked for, or that you’ve already discussed, in an issue.

A pull request doesn’t have to represent finished work. It’s usually better to open a pull request early on, so others can watch or give feedback on your progress. Just mark it as a “WIP” (Work in Progress) in the subject line. You can always add more commits later.

Always reference the issue related to the PR with `#number-of-issue` and use the markdown to make your comments more readable.

> **Note:** If this is your first pull request, check out [Make a Pull Request](http://makeapullrequest.com/), which [**@kentcdodds**](https://github.com/kentcdodds) created as a walkthrough video tutorial. You can also practice making a pull request in the [First Contributions](https://github.com/Roshanjossey/first-contributions) repository, created by [**@Roshanjossey**](https://github.com/Roshanjossey).

## Coding conventions

**Adhere to standard Python style guidelines**
All contributions to Netpyne are checked against style guidelines described in PEP 8. We also check for common coding errors (such as variables that are defined but never used).

Several text editors or IDEs also have Python style checking, which can highlight style errors while you code (and train you to make those errors less frequently). This functionality is built-in to the Spyder IDE, but most editors have plug-ins that provide similar functionality. Search for `python linter <name of your favorite editor>` to learn more.

**Use consistent variable naming**
Classes should be named using `CamelCase`. Functions and instances/variables should use `snake_case` (`n_samples` rather than `nsamples`). Avoid single-character variable names, unless inside a [comprehension](https://docs.python.org/3/glossary.html#term-list-comprehension) or [generator](https://docs.python.org/3/tutorial/classes.html#tut-generators).

**Follow NumPy style for docstrings**
In most cases imitating existing docstrings will be sufficient, but consult the [Numpy docstring style guidelines](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt) for more complicated formatting such as embedding example code, citing references, or including rendered mathematics. Private function/method docstrings may be brief for simple functions/methods, but complete docstrings are appropriate when private functions/methods are relatively complex.

**Other style guidance**

* Add description, arguments and returns (I/O params) to all functions and methos.
* Both the docstrings and dedicated documentation pages (readme file, tutorials, how-to examples, discussions, and glossary) should include cross-references to any mentioned module, class, function, method, attribute, or documentation page.
* We use [Travis](https://travis-ci.org/) to test code.
* Use a code checker:
  * [pylint](https://pypi.org/project/pylint/): a  Python static code analysis tool.
  * [pyflakes](https://pypi.python.org/pypi/pyflakes/):a tool to check Python code for errors by parsing the source file instead of importing it.
  * [pycodestyle](https://pypi.org/project/pycodestyle/): (formerly `pep8`) a tool to check Python code against some of the style conventions in PEP 8.
  * [flake8](https://pypi.org/project/flake8/): a tool that glues together `pycodestyle`, `pyflakes`, `mccabe` to check the style and quality of Python code.
  * [vim-flake8](https://github.com/nvie/vim-flake8): a `flake8` plugin for Vim.

<!-- Links References -->

<!--[NlN-repo]: (https://github.com/Neurosim-lab/netpyne)
[GH-fork]: (https://help.github.com/en/articles/fork-a-repo)
[GH-pr]: (https://help.github.com/en/articles/creating-a-pull-request)
[GH-push]: (https://help.github.com/en/articles/pushing-commits-to-a-remote-repository)
[GH-prfork]: (https://help.github.com/en/articles/creating-a-pull-request-from-a-fork)
[GH-start]: (https://guides.github.com/activities/hello-world/)
[GH-netpyne]: (https://github.com/Neurosim-lab/netpyne)
[GH-help]: (https://help.github.com/en)
[GH-llab]: (https://lab.github.com/)
[GH-issue]: (https://help.github.com/en/articles/creating-an-issue) -->