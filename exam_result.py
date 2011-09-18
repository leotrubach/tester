import sqlite3
import settings
from datetime import date,  timedelta

class ResultsBase(object):
    def __init__(self):
        self.conn = sqlite3.connect(settings.DATABASE)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS results (dt_exam, employee, correct, total, reportfile)''')
    
    def results_for_month(self,  year,  month):
        start_date = date(year,  month, 1)
        if month == 12:
            end_date = date(year+1,  1,  1)
        else:
            end_date = date(year,  month + 1,  1)
        c = self.conn.cursor()
        c.execute('SELECT * FROM results WHERE (dt_exam >= ?) AND (dt_exam < ?)',  [start_date,  end_date])
        for t in c:
            yield t
            
    def results_for_day(self,  year,  month,  day):
        start_date = date(year,  month, day)
        end_date = start_date + timedelta(days=1)
        c = self.conn.cursor()
        c.execute('SELECT * FROM results WHERE (dt_exam >= ?) AND (dt_exam < ?)',  [start_date,  end_date])
        for t in c:
            yield t
    
    def store(self,  dt_exam,  employee,  correct,  total,  reportfile):
        c = self.conn.cursor()
        c.execute('INSERT INTO results VALUES (?, ?, ?, ?, ?)',  
                  [dt_exam,  employee,  correct,  total,  reportfile])
        self.conn.commit()
