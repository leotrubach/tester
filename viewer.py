from PyQt4 import QtGui
import sys
import settings
import exam_result
import testcodec

class ViewerWindow(QtGui.QMainWindow):
    def __init__(self,  parent=None):
        QtGui.QMainWindow.__init__(self,  parent)
        self.results_base = exam_result.ResultsBase()
        self.prepare()
        
    def prepare(self):
        self.layout = QtGui.QHBoxLayout()
        self.fsm = QtGui.QFileSystemModel()
        self.fsm.setRootPath(settings.READER_REPORTS)
        cw = QtGui.QWidget()
        self.setCentralWidget(cw)
        self.report_tree = QtGui.QTreeView()
        self.report_tree.setModel(self.fsm)
        self.report_tree.setRootIndex(self.fsm.index(settings.READER_REPORTS))
        self.report_tree.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.report_tree.selectionModel().selectionChanged.connect(self.show_report)
        self.report_tree.hideColumn(1)
        self.report_tree.hideColumn(2)
        self.report_tree.hideColumn(3)
        self.report_view = QtGui.QTextEdit()
        
        self.layout.addWidget(self.report_tree)
        self.layout.addWidget(self.report_view)
        
        self.centralWidget().setLayout(self.layout)
        
    def show_report(self,  selected,  deselected):
        idx = selected.indexes()[0]
        filename = self.fsm.filePath(idx)
        print(filename)
        if not filename.endswith('.rep'):
            return
        f = open(filename)
        key = f.readline()
        encoded_text = f.read()
        f.close
        plain_text = testcodec.decode_text(encoded_text,  key)
        self.report_view.setText(plain_text)
        
    def day_summary(self,  path):
        s  = ''
        #for r in results:
        #    s = s + ' '.join(r) + '\n'
        self.report_view.setText(s)
    
app = QtGui.QApplication(sys.argv)
viewer = ViewerWindow()
viewer.show()
sys.exit(app.exec_())
