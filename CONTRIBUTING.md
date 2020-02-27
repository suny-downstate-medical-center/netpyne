
# NetPyNE Contribution Guidelines

## Table of Contents

- [NetPyNE Overview](#netpyne-overview)
- [Opening an Issue](#opening-an-issue-in-netpyne)
  - [Issue types](#issue-types)
    - [Bug reports](#bug-reports)
    - [Documentation improvements](#documentation-improvements)
    - [Feature requests](#feature-requests)
    - [Questions](#questions)
    - [Other Issues](#other-issues)
- [Submitting Improvements](#submitting-improvements-to-netpyne)
  - [Forking the NetPyNE repo](#forking-the-netpyne-repo)
  - [Cloning your fork locally](#cloning-your-fork-locally)
  - [Synchronizing your fork and clone](#synchronizing-your-fork-and-clone)
  - [Making changes to your clone](#making-changes-to-your-clone)
  - [Committing the changes](#committing-the-changes)
  - [Pushing to your fork](#pushing-to-your-fork)
  - [Making a pull request](#making-a-pull-request)
- [NetPyNE Coding Conventions](#netpyne-coding-conventions)


## NetPyNE Overview

Thank you for your interest in contributing to the NetPyNE Python package!  We encourage contributions to NetPyNE from individuals at all levels -- students, postdocs, academics, industry coders, hobbyists, etc.  For more information about NetPyNE, please see this [detailed overview](http://netpyne.org/overview.html) or our [eLife article](https://elifesciences.org/articles/44494).

NetPyNE is open-source and available in a GitHub repository at https://github.com/Neurosim-lab/netpyne, with detailed documentation at http://netpyne.org.  There is also a [Google Groups Q&A forum](https://groups.google.com/forum/#!forum/netpyne-forum) and a [NEURON/NetPyNE forum](https://www.neuron.yale.edu/phpBB/viewforum.php?f=45).

There is a separate [GitHub repository](https://github.com/Neurosim-lab/NetPyNE-UI) for the NetPyNE graphical user interface with its own [documentation](https://github.com/Neurosim-lab/NetPyNE-UI/wiki).  

NetPyNE is currently being developed and supported by the [Neurosim lab](http://neurosimlab.org/) and accepts contributions in the form of bug reports and fixes, feature requests and additions, and documentation improvements (even just typo corrections).  The best way to start contributing is by opening an [issue](https://github.com/Neurosim-lab/netpyne/issues).  If you're ready to contribute more directly to the project, please read on to learn the process for submitting improvements to the repository and opening a [pull request](https://github.com/Neurosim-lab/netpyne/pulls).

We ask that NetPyNE users and contributors adhere to our [Code of Conduct](https://github.com/Neurosim-lab/netpyne/blob/development/CODE_OF_CONDUCT.md) and [Coding Conventions](#coding-conventions).

> **Note:** This guide assumes you already have Git installed and configured on your machine.  If this is not the case, please see [Set up Git](https://help.github.com/en/github/getting-started-with-github/set-up-git) in [GitHub Help](https://help.github.com/en) for detailed Git installation and configuration instructions.  

## Opening an Issue in NetPyNE

The best way to start contributing to NetPyNE is by opening an [issue](https://github.com/Neurosim-lab/netpyne/issues).

> **Note:** See [creating an issue](https://help.github.com/en/articles/creating-an-issue) in [GitHub Help](https://help.github.com/en) for detailed instructions.

1. Go to the [NetPyNE GitHub repo](https://github.com/Neurosim-lab/netpyne).
2. Click on the "Issues" tab and then click on "New issue".
3. Choose the type of issue you would like to submit.
4. Provide a brief, informative title and a clear and concise description of the issue.
5. Click on "Submit new issue".

### Issue types

You can open an issue to report a bug, suggest improvements in documentation, request a new feature, ask a general question, or to discuss high-level topics or ideas.

#### Bug reports

Before submitting a bug report, please first check existing [bug reports](https://github.com/Neurosim-lab/netpyne/labels/bug) to see if the problem has already been reported.  If it has, please add a comment to the existing issue.

Have you tested on the latest version of NetPyNE?  If not, please [upgrade NetPyNE to the latest version](http://netpyne.org/install.html#upgrade-to-the-latest-released-version-of-netpyne-via-pip) and ensure the bug still exists.

If the bug hasn't been reported previously and you're using the latest version of NetPyNE, then please submit a bug report using the following guidelines:

* Create a brief, informative title
* Provide a clear and concise description of the bug
* Describe the exact steps that will reproduce the bug
* Explain the behavior you expected to see
* Provide information about your system:
  * Operating system and version
  * NetPyNE version (see `CHANGES.md` for version)
  * NEURON version (run `nrniv --version` in a terminal)
  * Python version (run `python --version` in a terminal)
* Describe any additional context needed to understand the bug

#### Documentation improvements

We are constantly striving to improve the [documentation](http://netpyne.org/) for NetPyNE.  If anything isn't clear, enough information isn't provided, or you have an idea for a tutorial or example, please submit a documentation improvement issue.

Please provide a clear and concise description of the desired documentation improvement for a specific function, a process, a tutorial, or even a simple typo.

#### Feature requests

Before submitting a feature request issue, please check the [NetPyNE documentation](http://netpyne.org/) to ensure it doesn't already exist, and check the [existing feature requests](https://github.com/Neurosim-lab/netpyne/labels/enhancement) to ensure nobody has already requested your desired feature.  If someone has already requested a feature similar to your idea, please add a comment to that issue rather than creating a new one.

If the feature doesn't already exist and nobody has requested it before, then please submit a feature request issue using the following guidelines:

* Create a brief, informative title
* Provide a clear and concise description of the requested feature
* If your feature is related to a problem:
  * Provide a clear and concise description of the problem, e.g. "I'm frustrated when [...]"
  * Explain the solution you would like to see
  * Describe any alternate solutions you've considered
* Provide any additional context needed to understand the feature request

#### Questions

Questions about NetPyNE are best sent to the [Google Groups Q&A forum](https://groups.google.com/forum/#!forum/netpyne-forum) or the [NEURON/NetPyNE forum](https://www.neuron.yale.edu/phpBB/viewforum.php?f=45), so that they are available to the entire NetPyNE community.  Please consider asking any questions you may have on an open forum before submitting a question here.

#### Other Issues

If you have any ideas for improvement of NetPyNE that don't fall into any of the other categories, please submit them as "Other issues".  This would be a good place to discuss a high-level topic or idea (for example: community, vision, or policies).

## Submitting Improvements to NetPyNE

If you are using NetPyNE and would like to contribute directly to the project, here's the place to find out how.  We encourage contributions to NetPyNE from individuals at all levels -- students, postdocs, academics, industry coders, hobbyists, etc.

In general, you’ll be working with three different copies of the NetPyNE repository codebase: the official remote copy at https://github.com/Neurosim-lab/netpyne (usually called `upstream`), your remote fork of the upstream repository (usually called `origin`), and the local clone (copy) of your remote fork on your computer.  All contributions to NetPyNE are added to the `development` branch, and later incorporated into the `master` branch at regular intervals for each new NetPyNE stable release.

The process for contributions is: fork the NetPyNE repo, clone it to your local machine, switch to the development branch, link your clone to the original NetPyNE repo, ensure your fork and clone are synchronized with the original repo, create a new branch for your changes, make the changes, commit those changes, push the commit to your fork, and make a pull request.  These steps are described in detail next.

### Forking the NetPyNE repo

All changes to the NetPyNE repo (repository) must be submitted from your own fork (copy) of the repo.

> **Note:** See [fork a repo](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) in [GitHub Help](https://help.github.com/en) for detailed instructions.  

Log into your GitHub account and navigate to the [NetPyNE repo](https://github.com/Neurosim-lab/netpyne).  In the upper right corner of the page, click on "Fork".  

The original NetPyNE repository is located at `https://github.com/Neurosim-lab/netpyne` while your fork will be located at `https://github.com/[your-GitHub-username]/netpyne`.

Changes are constantly being added to the NetPyNE repository, so it is essential that you ensure your fork is synchronized with the original repo before making any changes of your own.  If you have an existing fork of NetPyNE and haven't made any changes you want to keep, the easiest way to synchronize with the original repo is to delete your fork and create a new one.  To delete your fork, navigate to its webpage (https://github.com/[your-GitHub-username]/netpyne), click on "Settings", then under "Danger Zone" click on "Delete this repository" and follow the directions.  Be sure to delete any local clones of your NetPyNE fork as well.

> **Note:** See [deleting a repository](https://help.github.com/en/github/administering-a-repository/deleting-a-repository) in [GitHub Help](https://help.github.com/en) for detailed instructions.

### Cloning your fork locally

In order to work with the NetPyNE codebase, you must get a clone (copy) of your remote fork into your local machine.

> **Note:** See [cloning a repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) in [GitHub Help](https://help.github.com/en) for detailed instructions.

Navigate in your browser to your fork of NetPyNE (`https://github.com/[your-GitHub-username]/netpyne`).  Under the repository name, click "Clone or download".  Copy the URL under "Clone with HTTPS".  Open a Terminal on your machine and change directories to where you want the clone (e.g. `mkdir ~/github_repos; cd ~/github_repos`).  Type `git clone ` (note the space after "clone"), paste the copied URL, and press Enter.  Your local clone will be created (e.g. `~/github_repos/netpyne`).

At this point, your clone is only linked to your fork of NetPyNE.  Open a Terminal, change to the directory of your fork (e.g. `cd ~/github_repos/netpyne`), and enter `git remote -v` to see this.  Remember that your fork is called `origin` while the original NetPyNE repository is called `upstream`.

In a Terminal, from the directory of your clone, enter the following to link your clone to the original NetPyNE repository: `git remote add upstream https://github.com/Neurosim-lab/netpyne`.  Verify that your clone is linked by entering the command `git remote -v`.

Ensure that you are in the `development` branch of your clone by entering the command `git checkout development`.

### Synchronizing your fork and clone

Before you start making changes to the codebase in your clone, it is necessary to ensure that your clone and your fork are synchronized with the original NetPyNE codebase, to avoid conflicting changes.

> **Note:** See [syncing a fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork) in [GitHub Help](https://help.github.com/en) for detailed instructions.  Remember that instead of working with the `master` branch, you will be working with the `development` branch.

Open a Terminal and change to the directory of your NetPyNE clone.  Fetch any changes in the original NetPyNE repository by entering `git fetch upstream`.  Ensure you are in the `development` branch by entering `git checkout development`.  Now merge any changes from the original repo into your clone by entering `git merge upstream/development`.  

### Making changes to your clone

At this point, you have forked the NetPyNE repo, cloned it to your local machine, switched to the development branch, linked your clone to the original NetPyNE repo, and ensured your fork and clone are synchronized with the original repo.  Now it's time to actually make improvements to the code or documentation.

It's good practice to create a new branch for each improvement you'd like to make.  This keeps your local `development` branch the same as in your fork (i.e. clean and safe).  To create a new branch, open a Terminal and change to the directory of your clone.  Then enter `git checkout -b [name-of-your-new-branch]`.  

> **Note:** You can also [create a new branch directly on GitHub](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository).  You will then need to enter `git fetch origin` to get the new branch into your local clone and `git checkout [name-of-your-new-branch]` to switch to your new branch. 

At this point, you can use the code editor of your choice to make changes to any of the files in your clone.  [Visual Studio Code](https://code.visualstudio.com/) and [Sublime Text](https://www.sublimetext.com/) are popular choices.  After making changes, be sure the code still runs and behaves as you expect.

### Committing the changes

Once you've made changes and tested them, it's time to commit them to your local clone.  Open a Terminal and change to the directory of your clone.  Enter `git status` to see what files have been changed.  Enter `git add [filename]` to stage (prepare) a particular file for committing or `git add .` to stage all changed files.  Enter `git status` again to ensure the file(s) you want to commit are ready.  Finally, to commit the changes to your local clone, enter `git commit -m "[A concise description of your changes]"` (include the quotes but not the brackets).  

> **Note:** You can also just enter `git commit`.  Git will then open your Terminal's default text editor and ask you to enter a commit message (e.g. [A concise description of your changes]).

### Pushing to your fork

Now that you have your changes committed to your local clone, it's time to push them to your remote fork on GitHub.  In a Terminal, from the directory of your clone, enter `git push origin name-of-your-new-branch`.

> **Note:** See [pushing commits to a remote repository](https://help.github.com/en/github/using-git/pushing-commits-to-a-remote-repository) in [GitHub Help](https://help.github.com/en) for detailed instructions.  

### Making a pull request

Now that you've got your improvements into your remote fork of NetPyNE on GitHub, it's time to submit the improvements to the original NetPyNE repository.  This is accomplished by creating a "pull request".

> **Note:** See [creating a pull request from a fork](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-forkk) in [GitHub Help](https://help.github.com/en) for detailed instructions.

In your browser, go to https://github.com/Neurosim-lab/netpyne and click on the "New pull request" button
.  This will bring you to the "Compare changes" page where you should click on "compare across forks".  Ensure the "base repository" is `Neurosim-lab/netpyne` and the "base" is `development`.  Set the head repository as `[your-GitHub-username]/netpyne` and the "compare" is `[name-of-your-new-branch]`.  Type a title and description for your pull request (if your modifications were in response to an issue, include the issue number).  Finally, click on "Create Pull Request".

> **Note:** A pull request doesn’t have to represent finished work.  It’s actually better to open a pull request early on, so others can give feedback on your progress.  Just mention in the description that it is a "Work in Progress". You can always add more commits later after discussions with the NetPyNE community.  Please see [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/) for an excellent overview of the process.

## NetPyNE Coding Conventions

**Adhere to standard Python style guidelines**

All contributions to NetPyNE are checked against style guidelines described in PEP 8 (we are gradually updating the existing code). We also check for common coding errors (such as variables that are defined but never used).

Several text editors or IDEs also have Python style checking, which can highlight style errors while you code (and train you to make those errors less frequently). This functionality is built-in to the Spyder IDE, but most editors have plug-ins that provide similar functionality. Search for `python linter <name of your favorite editor>` to learn more.

**Use consistent variable naming**

Functions and instances/variables should use `CamelCase` (`nSamples` rather than `n_samples`). Avoid single-character variable names, unless inside a [comprehension](https://docs.python.org/3/glossary.html#term-list-comprehension) or [generator](https://docs.python.org/3/tutorial/classes.html#tut-generators).

**Follow NumPy style for docstrings**

In most cases imitating existing docstrings will be sufficient, but consult the [NumPy docstring style guidelines](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt) for more complicated formatting such as embedding example code, citing references, or including rendered mathematics. Private function/method docstrings may be brief for simple functions/methods, but complete docstrings are appropriate when private functions/methods are relatively complex (we are gradually updating the code to include docstrings for all functions).

**Other style guidance**

* Add description, arguments and returns (I/O params) to all functions and methods.
* Both the docstrings and dedicated documentation pages (readme file, tutorials, how-to examples, discussions, and glossary) should include cross-references to any mentioned module, class, function, method, attribute, or documentation page.
* We use [Travis](https://travis-ci.org/) as a continuous integration tool, to run tests after every commit to check that the model examples still work and produce the expected result.
* Use a code checker:
  * [pylint](https://pypi.org/project/pylint/): a Python static code analysis tool.
  * [pyflakes](https://pypi.python.org/pypi/pyflakes/): a tool to check Python code for errors by parsing the source file instead of importing it.
  * [pycodestyle](https://pypi.org/project/pycodestyle/): (formerly `pep8`) a tool to check Python code against some of the style conventions in PEP 8.
  * [flake8](https://pypi.org/project/flake8/): a tool that glues together `pycodestyle`, `pyflakes`, and `mccabe` to check the style and quality of Python code.
  * [vim-flake8](https://github.com/nvie/vim-flake8): a `flake8` plugin for Vim.
