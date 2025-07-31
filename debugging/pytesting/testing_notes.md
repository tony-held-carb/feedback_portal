Prompt to cursor:

on my home machine i ran
pytest tests/arb -v  > "pytest_${MACHINE_NAME}_all_21.txt" 2>&1
pytest -s tests/e2e -v  > "pytest_${MACHINE_NAME}_e2e_21.txt" 2>&1

on the ec i ran
pytest tests/arb -v  > "pytest_${MACHINE_NAME}_all_21.txt" 2>&1

on my work machine, i ran
pytest tests/arb -v  > "pytest_${MACHINE_NAME}_all_21.txt" 2>&1
pytest -s tests/e2e -v  > "pytest_${MACHINE_NAME}_e2e_21.txt" 2>&1

i launched the portal flask app on my ec serving at: http://10.93.112.44:2113/
i updated:
# TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://127.0.0.1:2113")
TEST_BASE_URL = os.environ.get('TEST_BASE_URL', "http://10.93.112.44:2113/")

and then from my work machine, i ran the e2e tests on the ec2 server (since i can run e2e on the ec2 directly)
pytest tests/e2e -v  > "pytest_flask_on_ec2_testing_on_work_e2e_21.txt" 2>&1

Please analyze and lets fix the testing if necessary.

The results are located here:



Thu, Jul 31, 2025  6:56:29 AM
- updated e2e last night to make it more robust
- running tests on home, work, ec2 using demo database and saving to tests_02
- looks like most are passing, maybe a few minor testing issues
- going to decide to fix the testing or switch to testing on the real database and just make notes on the fails
- would like to change the waiting system so that it was more robust, but that may be a future fix

Thu, Jul 31, 2025  8:21:30 AM
tests_03 are running on real portal database


