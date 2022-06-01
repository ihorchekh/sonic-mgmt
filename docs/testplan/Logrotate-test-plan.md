# Logrotate test plan

* [Goal](#goal)
* [Scope](#scope)
* [Testbed](#testbed)
* [Setup configuration](#setup-configuration)
* [Test cases](#test-cases)
* [TODO](#todo)
* [Open questions](#open-questions)

## Goal
The purpose is to test functionality of the log rotate feature on the SONIC switch DUT.

## Scope
The test is targeting a running SONIC system with fully functioning configuration.

## Testbed
The test will run on the all testbeds, not depending on topology

## Setup configuration
No setup pre-configuration is required.

## Test cases

### Test case #1 – Logrotate positive test - when a log file is over the threshold
#### Test objective
Verify logrotate works when the log size is over the threshold.
#### Test steps
* Select one random log from the list of logs specified in /etc/logrotate.d/rsyslog
* Increase size to the threshold - 16M.
* Execute the logrotate
* The test is PASSED if the new size is less than before the logrotate.

### Test case #2 – Logrotate negative test - when a log file is small
#### Test objective
Verify logrotate doesn't work when the log size is 10K.
#### Test steps
* Select the same log from the previous step.
* Set the size to 10K.
* Execute the logrotate
* The test is PASSED if the new size is not less than before the logrotate.

### Test case #3 – Logrotate negative test - when a log file is big, but below the threshold
#### Test objective
Verify logrotate doesn't work when the log size is 8M.
#### Test steps
* Select the same log from the previous step.
* Set the size to 8M.
* Execute the logrotate
* The test is PASSED if the new size is not less than before the logrotate.

## TODO

## Open questions