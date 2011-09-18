from PyQt4 import QtGui, QtCore
from quiz import TestLoader, write_to_log
from driverbase import DriverBase
import gettext
import hashlib
import settings
import os

locale_path = os.path.join(settings.PROG_DIR, 'locale')
gettext.install('messages', locale_path)

lan_ru = gettext.translation('messages', locale_path, languages=['ru'])
lan_ru.install()
_ = lan_ru.gettext

def createIntroPage():
    page = QtGui.QWizardPage()
    page.setTitle(_("Introduction"))

    label = QtGui.QLabel(_("Welcome to Tester. Press Next button to start"))
    label.setWordWrap(True)

    layout = QtGui.QVBoxLayout()
    layout.addWidget(label)
    page.setLayout(layout)

    return page

class NumPadButton(QtGui.QPushButton):
    def sizeHint(self):
        size = QtGui.QPushButton.sizeHint(self)
        size.setHeight(size.height() + 50)
        size.setWidth(size.height())
        return size

class NumPadWidget(QtGui.QWidget):

    numkeyPressed = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.bletters = [['1','2','3'],
                         ['4','5','6'],
                         ['7','8','9'],
                         ['X','0','OK']]
        self.prepare()

    def make_typer(self, letter):
        
        def typer():
            self.numkeyPressed.emit(letter)

        return typer

    def prepare(self):
        vl = QtGui.QVBoxLayout()
        font = QtGui.QFont('Ubuntu', 18, QtGui.QFont.Bold)
        for row in self.bletters:
            hl = QtGui.QHBoxLayout()
            for letter in row:
                b = NumPadButton(letter)
                b.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
                b.setFont(font)
                b.clicked.connect(self.make_typer(letter))
                hl.addWidget(b)
            hl.addStretch()
            vl.addLayout(hl)
        self.setLayout(vl)


class RegistrationPage(QtGui.QWizardPage):

    def prepare(self, ts):
        self.tabnum = ''
        self.ts = ts
        self.complete = False
        self.frozen = False
        self.setTitle(_('Registration'))
        self.setSubTitle(_('Please enter your information'))

        self.layout = QtGui.QFormLayout()
        self.nameLineEdit = QtGui.QLineEdit()
        self.passwordLineEdit = QtGui.QLineEdit()
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.numpad = NumPadWidget()
        self.numpad.numkeyPressed.connect(self.numpadkey)
        self.commit = QtGui.QCheckBox()
        self.commit.hide()
        self.commit.setChecked(False)
        self.commit.stateChanged.connect(self.confirm_checked)

        self.start_test = QtGui.QPushButton(_('Start test'))
        self.start_test.pressed.connect(self.promote)
        self.start_test.hide()
        
        self.layout.addRow(_('Enter your table number:'), self.nameLineEdit)
        self.layout.addRow('', self.numpad)
        self.layout.addRow('', self.commit)
        self.layout.addRow('', self.start_test)
        self.setCommitPage(True)

        self.setLayout(self.layout)

    def promote(self):
        self.wizard().next()

    def isComplete(self):
        return self.complete

    def set_db(self, db):
        self.db = db

    def ok_pressed(self):
        driver_name = self.db.get_driver(self.tabnum)
        if driver_name:
            self.nameLineEdit.setEnabled(False)
            self.commit.setText(_('I CONFIRM THAT I AM {name}').format(name=driver_name))
            self.commit.show()
            self.frozen = True
        else:
            self.commit.hide()
    
    def confirm_checked(self):
        if self.commit.isChecked():
            self.complete = True
            self.completeChanged.emit()
            self.start_test.show()
        else:
            self.complete = False
            self.completeChanged.emit()
            self.start_test.hide()

    def numpadkey(self, s):
        if s == 'X':
            self.tabnum = ''
            self.nameLineEdit.setEnabled(True)
            self.commit.setChecked(False)
            self.commit.hide()
            self.complete = False
            self.frozen = False
            self.completeChanged.emit()
        elif s == 'OK':
            self.ok_pressed()
        else:
            if not self.frozen:
                self.tabnum += s
        self.nameLineEdit.setText(self.tabnum)

    def validatePage(self):
        driver_name = self.db.get_driver(self.tabnum)
        if not driver_name:
            return False
        else:
            self.ts.user = driver_name 
            return True


def createRegistrationPage():
    page = RegistrationPage()
    page.prepare(ts)
    page.set_db(db)
    return page

def createCommitPage():
    page = QtGui.QWizardPage()
    page.setTitle(_('Last chance'))

    label = QtGui.QLabel(_('Press commit button to get the results of test'))
    label.setWordWrap(True)

    layout = QtGui.QVBoxLayout()
    layout.addWidget(label)
    page.setLayout(layout)
    page.setCommitPage(True)

    return page

class ConclusionPage(QtGui.QWizardPage):
    def prepare(self, ts):
        self.ts = ts
        self.setTitle(_("Conclusion"))

        label = QtGui.QLabel(_("Done "))
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        if settings.SHOW_REPORT:
            self.logText = QtGui.QPlainTextEdit()
            layout.addWidget(self.logText)
        else:
            layout.addWidget(QtGui.QLabel(_('Thanks for submitting test results. Your results are sent to administration')))
        self.setLayout(layout)

    def initializePage(self):
        if settings.SHOW_REPORT:
            self.logText.setPlainText(ts.log())
        logname = write_to_log(ts.log())
        ts.set_logname(logname)

def createConclusionPage():
    page = ConclusionPage()
    page.prepare(ts)
    return page

class QuestionPage(QtGui.QWizardPage):

    def setQuestion(self, ts, qnum):
        self.ts = ts
        self.qnum = qnum
        q = ts.questions[qnum]
        font = QtGui.QFont('Ubuntu', 16, QtGui.QFont.Bold)
        qtext = QtGui.QLabel(q.body)
        qtext.setWordWrap(True)
        qtext.setFont(font)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(qtext)
        layout.addSpacing(20)
        self.bgAnswers = QtGui.QButtonGroup()
        self.bgAnswers.buttonPressed[int].connect(self.updateAnswer)
        self.qnum = qnum
        i = 0
        for a in q.answers:
            hl = QtGui.QHBoxLayout()
            b = QtGui.QToolButton()
            b.setCheckable(True)
            l = QtGui.QLabel(a[0])
            l.setWordWrap(True)
            hl.addWidget(b)
            hl.addWidget(l)
            layout.addLayout(hl)
            self.bgAnswers.addButton(b, i)
            i += 1
        self.setLayout(layout)

    def updateAnswer(self, ans_id):
        self.ts.set_answer(self.qnum, ans_id)


class TestWizard(QtGui.QWizard):
    def closeEvent(self, event):
        if self.test_password():
            event.accept()
        else:
            event.ignore()

    def test_password(self):
        pi = QtGui.QInputDialog()
        pi.setTextEchoMode(QtGui.QLineEdit.Password)
        pi.setInputMode(QtGui.QInputDialog.TextInput)
        pi.setLabelText(_('Enter password to close tester'))
        pi.setWindowTitle(_('Password request'))
        if pi.exec() == QtGui.QDialog.Rejected:
            return False

        t = pi.textValue()
        if (hashlib.sha256(t.encode()).hexdigest() == settings.PASSWORD):
            return True
        else:
            return False 

    def reject(self):
        if self.test_password():
            QtGui.QWizard.reject(self)
        
def createQuestionsPage(ts):
    pages = []
    for i in range(len(ts.questions)):
        page = QuestionPage()
        page.setTitle(_("Question {n}").format(n=i+1))
        page.setQuestion(ts, i)
        pages.append(page)
    return pages

if __name__ == '__main__':
    import sys
    if not os.path.exists(settings.KEYFILE):
        sys.exit()

    db = DriverBase(os.path.join(settings.PROG_DIR, 'drivers.dat'))
    test = TestLoader(os.path.join(settings.PROG_DIR, settings.TESTFILEDIR, settings.DEFAULTTEST))
    app = QtGui.QApplication(sys.argv)
    font = QtGui.QFont('Ubuntu', 14)
    app.setFont(font)
    app.setStyleSheet('QToolButton:checked {background-color: blue; border-style:inset}')

    while True:
        ts = test.produce_testsuite() 
        wizard = TestWizard()
        wizard.setOption(QtGui.QWizard.NoCancelButton, True)
        wizard.setWindowState(QtCore.Qt.WindowFullScreen)
        #wizard.addPage(createIntroPage())
        wizard.addPage(createRegistrationPage())
        for page in createQuestionsPage(ts):
            wizard.addPage(page)
        wizard.addPage(createCommitPage())
        wizard.addPage(createConclusionPage())
        wizard.setWindowTitle("Tester")
        wizard.setButtonText(QtGui.QWizard.NextButton, _('Next'))
        wizard.setButtonText(QtGui.QWizard.BackButton, _('Back'))
        wizard.setButtonText(QtGui.QWizard.FinishButton, _('Finish'))
        wizard.setButtonText(QtGui.QWizard.CommitButton, _('Commit'))
        if wizard.exec() == QtGui.QDialog.Rejected:
            break
        test.results_base.store(ts.dt_exam,  ts.user,  len(ts.questions),  ts.test_results(),  ts.logname)
