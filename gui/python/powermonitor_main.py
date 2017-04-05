"""
The main class for the project PowerMonitor.
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.main import Main


# import gui from qt designer
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    main = Main()
    main.showMaximized()
    
    # import object debug code (remove if not needed)
    #import pdb; pdb.set_trace()

    sys.exit(app.exec_())