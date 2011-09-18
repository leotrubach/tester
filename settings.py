import os

QBASEDIR = 'qbases'            # Directory with questions databases
TESTFILEDIR = 'tests'          # Directory with test files
REPORTDIR = 'report'           # Directory with reports
READER_REPORTS = r'\\10.129.13.240\report$'
DEFAULTTEST = 'mashinist.txt'  # Default test filename
PASS_PERCENTAGE = 50           # Percentage which is needed to be answered
                               # to allow user pass exam
PASSWORD='24fd7e2735af185459f293eb8704789722c8e46ef86c880322577fe019bb829c'                # Password to close Tester
SHOW_REPORT=True               # Show report at the end of testing
KEYFILE=r'C:\Windows\test.dat'
PROG_DIR=os.path.split(__file__)[0]
DATABASE='blah.db' #os.path.join(READER_REPORTS,  'results.sqlite')

