import random
import gettext
import testcodec
import os
import settings
import datetime
import exam_result

locale_path = os.path.join(settings.PROG_DIR, 'locale')
lan_ru = gettext.translation('messages', locale_path, languages=['ru'])
lan_ru.install()
_ = lan_ru.gettext

class Question(object):
    def __init__(self, body, answers):
        self.body = body
        self.answers = answers

    def shuffle(self):
        random.shuffle(self.answers)

    def __unicode__(self):
        r = []
        i = 0
        for a in self.answers:
            i += 1
            r.append('{0}) {1}'.format(i, a[0]))

        return '{q}\n{a}'.format(q=self.body, a = '\n'.join(r))


class TestSuite(object):
    def __init__(self, user = None, questions = []):
        self.user = user
        self.questions = []
        if questions:
            self.questions += questions
        
        self.user_answers = [-1]*len(self.questions)
    
    def add_questions(self, questions):
        self.questions += questions
        self.user_answers += [-1]*len(questions)

    def test_results(self):
        points = 0
        for i in range(len(self.questions)):
            if self.user_answers[i] != -1:
                points += self.questions[i].answers[self.user_answers[i]][1]
        return points

    def set_answer(self, i, a):
        self.user_answers[i] = a
    
    def set_logname(self,  logname):
        self.logname = logname

    def log(self):
        total = 0
        points = 0
        s = ''
        self.dt_exam = datetime.datetime.now()
        s += _('TIMESTAMP: {ts}\n').format(ts = self.dt_exam.strftime('%d/%m/%Y %H:%M:%S'))
        s += _('User: {user}\n').format(user=self.user)
        for i in range(len(self.questions)):
            s += _('QUESTION: {q}\n').format(q = self.questions[i].body)
            if self.user_answers[i] == -1:
                s += _('ANSWER: not given\n\n')
                points = 0
            else:
                s += _('GIVEN ANSWER: {a}\n').format(a = self.questions[i].answers[self.user_answers[i]][0])
                points = self.questions[i].answers[self.user_answers[i]][1]
                total += points
                s += _('POINTS: {p}\n\n').format(p = points)
        percentage = total*100/len(self.questions)
        s += _('TOTAL POINTS: {p}\n').format(p = total)
        s += _('CORRECT ANSWER PERCENTAGE: {p:.2f}%\n').format(p = percentage)
        if percentage >= settings.PASS_PERCENTAGE:
            s += _('EXAM PASSED\n')
        else:
            s += _('EXAM FAILED\n')
        s += '-'*30
        return s

def write_to_log(s):
    now = datetime.datetime.now()
    dstr = now.strftime('%Y\\%m\\%d')
    log_dir = os.path.join(settings.PROG_DIR, settings.REPORTDIR, dstr)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    filename = os.path.join(log_dir, now.strftime('%H%M%S') + '.rep')
    f = open(filename, 'w')
    k = testcodec.generate_key()
    r = testcodec.encode_text(s, k)
    f.write(k)
    f.write(r)
    f.close()
    return filename

class QuestionBase(object):

    def __init__(self):
        self.questions = []

    def load_questions(self, filename):
        if filename.endswith('.tst'):
            f = open(filename)
            k = f.readline()
            r = f.read()
            lines = testcodec.decode_text(r, k).split('\n')
        else:
            lines = open(filename).read().split('\n')
        self.import_questions(lines)

    def import_questions(self, lines):
        qlines = []
        answers = []
        for line in lines:
            if line.strip() == '':
                if qlines and answers:
                    body = '\n'.join(qlines)
                    q = Question(body, answers)
                    self.questions.append(q)
                qlines = []
                answers = []
            else:
                if line.startswith('?'):
                    qlines.append(line[1:].strip())
                elif line.startswith('+'):
                    answers.append((line[1:].strip(), 1))
                elif line.startswith('-'):
                    answers.append((line[1:].strip(), 0))

    def shuffle_questions(self):
        for q in self.questions:
            q.shuffle()

    def select_questions(self, qc):
        return random.sample(self.questions, qc)

class TestLoader(object):
    def __init__(self, testfile):
        self.sets = []
        self.results_base = exam_result.ResultsBase()
        for line in open(testfile):
            qbname, qnum = line.split(';')
            self.sets.append((qbname, qnum))

    def produce_testsuite(self):
        ts = TestSuite()
        for s in self.sets:
            qb = QuestionBase()
            qb.load_questions(os.path.join(settings.PROG_DIR, settings.QBASEDIR, s[0]))
            qb.shuffle_questions()
            qs = qb.select_questions(int(s[1]))
            ts.add_questions(qs)
        return ts

if __name__ == '__main__':
    qb = QuestionBase()
    qb.load_questions('questions.txt')
    qb.shuffle_questions()
    print(qb.questions)
    for q in qb.questions:
        print(q.__unicode__())

