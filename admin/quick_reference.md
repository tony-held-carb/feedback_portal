## Running pytests

0. it may be helpful to kill chrome before running tests to clear up memory and resources
   taskkill //f //im chrome.exe

1. Ensure you are in the root folder to run tests
   cd $portal

2. General pytest run
   pytest <file or folder> -v -s --maxfail=3 -k "match01 or match02"  --durations=0 | tee output_file_01.txt
   pytest <file or folder> -v -s --maxfail=3 -k "match01 or match02"  --durations=0 > output_file_01.txt 2>&1

2a. Common Tests Run
pytest tests/arb -v  > "pytest_${MACHINE_NAME}_arb_78.txt" 2>&1
pytest -s tests/e2e -v --durations=0  > "pytest_${MACHINE_NAME}_e2e_78.txt" 2>&1

2b. cursor recommended test pattern
please use this testing pattern
cd /d/local/cursor/feedback_portal && pytest <file or folder> <options>  | tee pytest_<description of test>.txt

3. Flag meanings:
   --maxfail=num Exit after first num failures or errors
   -v, --verbose Increase verbosity
   -s Don't suppress print statements that are in test files
   -k EXPRESSION Only run tests which match the given substring expression. An expression is a Python evaluable
   expression where all names are substring-matched against test names and their parent classes.
   Example: -k 'test_method or test_other' matches all test functions and classes whose name contains
   'test_method' or 'test_other', while -k 'not test_method' matches those that don't contain
   'test_method' in their names. -k 'not test_method and not test_other' will eliminate the matches.
   Additionally keywords are matched to classes and functions containing extra names in their
   'extra_keyword_matches' set, as well as functions which have names assigned directly to them. The
   matching is case-insensitive.
   --durations=0 Show timing for each test
   --durations=10 Show timing for slowest tests
   --durations=0 --tb=short Show timing with more detail
4. tee versus redirection
   | tee <filename>        you get terminal feedback of the tests while simultaneously sending to log file
   > <filename> 2>&1       captures standard output and error and may be more reliable in some situations

5. example runs:

   pytest tests/e2e/test_excel_upload_playwright_pytest.py --only-discard-tests -v | tee pytest_output_04.txt
   pytest tests/e2e/test_excel_upload_playwright_pytest.py -v --maxfail=3 | tee pytest_output_04.txt
   pytest tests/e2e/test_excel_upload_playwright_pytest.py -v | tee pytest_output_04.txt
   pytest tests/e2e/test_excel_upload_playwright_pytest.py -v --maxfail=3 -k "discard or malformed" | tee
   pytest_output_04.txt
   pytest tests/e2e/test_excel_upload_playwright_pytest.py -v -k "test_diagnostics_overlay_on_diagnostic_test_page" |
   tee pytest_output_04.txt
   pytest tests/e2e/test_diagnostics.py -v | tee pytest_diag_03.txt
   pytest tests/e2e/test_excel_upload_playwright_pytest.py -v -k "discard or malformed" | tee pytest_output_04.txt
   pytest tests/e2e/test_diagnostics.py -v | tee pytest_diag_28.txt
   pytest tests/e2e/test_diagnostics.py -v -k test_diagnostics_overlay_on_diagnostic_test_page | tee pytest_diag_12.txt
   pytest tests/e2e/test_feedback_updates.py -v > pytest_feedback_updates.txt 2>&1
   pytest tests/e2e -v | tee pytest_e2e_10.txt
   pytest tests/arb -v | tee pytest_all_07.txt
   pytest -s tests/arb/portal/test_file_upload_suite.py | tee pytest_06.txt

   mini_conda_01.yml original production environment interpreter
   mini_conda_02.yml updated to include playwright and other requirements

   7/22/25 5:37PM ec2 installed from  ~/mini_conda_02.yml
   7/22/25 5:43PM work computer from  "C:\tony_local\pycharm\feedback_portal\admin\mini_conda_02.yml"
   7/22/25 5:40PM home computer from  "D:\local\cursor\feedback_portal\admin\mini_conda_02.yml"

   pytest tests/arb -v  > pytest_laptop_all_16.txt 2>&1
   pytest tests/e2e -v  > pytest_laptop_e2e_16.txt 2>&1

## Environmental Variables

listing environmental variables on git bash
printenv | sort

To list only environment variables containing the word "root"
printenv | sort | grep root         (case-sensitive)
printenv | sort | grep -i root      (case-insensitive)

----------------------------------
Creating Environmental Variables
----------------------------------
Create an environmental variable in all systems named, MACHINE_NAME that can be "TONY_HOME", "TONY_WORK", or "TONY_EC2"

*** Windows ***

Single Variable
setx MACHINE_NAME "TONY_WORK"           (CMD or Git Bash)
setx MACHINE_NAME "TONY_HOME"           (CMD or Git Bash)

To prepend/append use the format
setx PATH "%PATH%;C:\your\new\path"     (CMD)
setx PATH "C:\your\new\path;%PATH%"     (CMD)

setx PATH "$PATH;/c/your/new/path"      (Git Bash)
setx PATH "$PATH;C:\your\new\path"      (Git Bash)

To check if it worked
echo %MACHINE_NAME%     (CMD)
echo "$MACHINE_NAME"    (Git Bash)

*** Linux EC2 ***
note that linux uses : not like windows ;

edit ~/.bashrc to include
export MACHINE_NAME="TONY_EC2"
export PATH="$PATH:/your/new/path"
export PATH="/your/new/path:$PATH"
source ~/.bashrc

To check if it worked
echo "$MACHINE_NAME"

Notes:

1. If you run the following and PATH is not already defined
   export PATH="$PATH:/your/new/path"
   PATH=":/your/new/path"
2. In linux a leading colon resolves  "include the current directory (.)"
3. If you only want to include the variable if it already exists
   export PATH="${PATH:+$PATH:}/your/new/path"
   ${PATH:+$PATH:} means:
   If PATH is defined → include $PATH:
   If PATH is undefined → insert nothing (no colon)
4. The PATH example is a little confusing because the colon is doing double duty, the more generalized syntax is:
   ${var:+value} is a parameter expansion operator
   If var is set and not null → return value
   If var is unset or null → return nothing
   export my_long_list="${my_long_list:+$my_long_list, }list item #10, list item #11"
   If my_long_list is already populated, you insert its current value plus a comma and space
   Then add new items at the end

You can use the linux style export on windows git bash, but it won't be persistent

## WSL and Windows Paths

If you're running WSL and your pwd shows:
/home/tonyh

Then in Windows Explorer, you can access that WSL path like this:
\\wsl$\Ubuntu\home\tonyh

Home computer my user is tonyh, on linux it is theld, it is very easy to get confused on the matter

                          Windows Path                        WSL Path
                          ------------                        --------
Windows Home Directory:   C:\Users\tonyh,                     /mnt/c/Users/tonyh
WSL Home Directory:       \\wsl$\Ubuntu\home\tonyh            /home/tonyh
Feedback Portal:          D:\local\cursor\feedback_portal     /mnt/d/local/cursor/feedback_portal
