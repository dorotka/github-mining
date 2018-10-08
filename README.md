# github-mining

The github-mining project contains a series of scripts that save and analyze data for the predefined repositories in order to analyze developers’ focus.
It was created to download the information used in the ​'Are Good Developers More Focused?' D​issertation included under dissertation folder.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

1. Create virtual environment:
    ```
	mkdir Environments
	cd Environments
	python3 -m venv my_env
	source my_env/bin/activate
	```

### Prerequisites

*Python3

```
example
```

###SCRIPT ORDER:

1.
load_repos.py
- Script clones selected repositories to the repos folder

2.
download_issues.py -u <owner> <project>
- Script must be run for each repository. It may take up to 30 min per repository.

3.
labels.py -u <owner> <project>
- Script must be run for each repository.

4.
setup_fixes.py
- Script must be run once. It runs each of the below scripts on every repository:
	* extract_bugs.py
	* extract_commits.py
	* extract_fixes.py

5.
extract_buggy_commits.py <project>
- Script must be run for each repository. It may take up to 30 min per repository.

6.
annotate_commits.py <project>
- Script must be run for each repository. It may take up to 30 min per repository.

7.
get_devs.py
- Script must be run once. It runs each of the following scripts:
	* prepare_devs.py (for each repository)
	* combine.py
	* select_devs.py
8.
analyze_focus.py
- Script must be run once.

###TO RUN VISUALIZATIONS:

If the submission was made without the data, you need to copy the following data files to the tools/visualization/data directory:
* toosl/data/authors_ratio.json
* tools/data/entropy_all.json
* tools/data/entropy_daily.json
* tools/data/entropy_yearly.json
* tools/data/entropy_per_dev.json
* tools/data/entropy_per_year.json
* tools/data/entropy_ext_distribution.json
* tools/data/entropy_ranges_vis.json
* tools/data/entropy_exts_popular.json
Further instructions are included in each html file under tools/visualization.


### Installing

TBA...
A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
example
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

*Add tools folder to the PYTHONPATH:
```
export PYTHONPATH=“<location of the folder>/tools:$PYTHONPATH"
```
*Run test scripts from tools folder as specified in the scripts usage:
```
python3 tests/<test_script>.py
```
*In order to run the tests, you need to have the test data. You need to run the scripts with test flag set to True in order to create the test data. By default test flag is set to False.

Test cases documentation is included in [the specs] (documentation/GFA_Specs_v4.pdf)

## Built With

* [Python3](https://www.python.org/download/releases/3.0/)
* [GitHub API](https://developer.github.com/v3/)

