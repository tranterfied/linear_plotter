from PyQt4 import QtCore
from PyQt4.QtGui import *
from scipy import stats
import string
import pyqtgraph as pg
import numpy as np

# set some default options
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

colours = ['5D8600', '0A213E', 'B33B16']

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # add the title
        self.setWindowTitle('EasyPlot -- Free Python Plotting Tool!')

        # the main widget and set it as the central widget
        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        # the main layout
        self.main_layout = QGridLayout(self.widget)

        # set the window size
        self.setMinimumSize(QtCore.QSize(800, 600))

        ## Data Table Structure ----------------------------------------------------
        # the main data table
        self.table_size = (1000, 12)
        self.data_table = QTableWidget()
        self.data_table.setRowCount(self.table_size[0])
        self.data_table.setColumnCount(self.table_size[1])
        self.data_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        # set the heading to the alphabet
        self.data_table.setHorizontalHeaderLabels(list(string.ascii_uppercase))
        # add to the main table
        self.main_layout.addWidget(self.data_table, 0, 0, 1, 3)
        # initialise the tables
        for i in range(self.table_size[0]):
            for j in range(self.table_size[1]):
                self.data_table.setItem(i,j, QTableWidgetItem(''))

        ## Combobox Structures ----------------------------------------------------
        # create a group box to hide the data entry in
        self.data_gb = QGroupBox()
        self.data_gb_layout = QFormLayout(self.data_gb)

        columns = list(string.ascii_uppercase)[0:self.data_table.columnCount()]
        self.dependent_box = QComboBox()
        self.dependent_box.addItems(columns)
        self.data_gb_layout.addRow('&Dependent Variable:', self.dependent_box)

        self.independent_box = QComboBox()
        self.independent_box.addItems(columns)
        self.data_gb_layout.addRow('&Independent Variable:', self.independent_box)

        self.y_error_box = QComboBox()
        self.y_error_box.addItems(columns)
        self.data_gb_layout.addRow('&Y Errors:', self.y_error_box)

        self.x_error_box = QComboBox()
        self.x_error_box.addItems(columns)
        self.data_gb_layout.addRow('&X Errors', self.x_error_box)

        self.main_layout.addWidget(self.data_gb, 2, 0, 1, 1)

        ## Data Range Structures ----------------------------------------------------
        # create an additional group box
        self.range_box = QGroupBox()
        self.range_box_layout = QFormLayout(self.range_box)
        self.range_box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.range_box.setMaximumWidth(200)

        self.start_range_box = QLineEdit()
        self.start_range_box.setValidator(QIntValidator())
        self.range_box_layout.addRow('&From:', self.start_range_box)

        self.end_range_box = QLineEdit()
        self.end_range_box.setValidator(QIntValidator())
        self.range_box_layout.addRow('&to:', self.end_range_box)

        self.main_layout.addWidget(self.range_box, 2, 1, 1, 1)

        ## Buttons! ------------------------------------------------------------------
        self.button_box = QGroupBox()
        self.button_box_layout = QVBoxLayout(self.button_box)
        self.main_layout.addWidget(self.button_box, 2, 2, 1, 1)
        self.button_box.setMinimumWidth(200)

        ## Linear fit button
        self.linear_fit_button = QPushButton('Linear Fit')
        self.button_box_layout.addWidget(self.linear_fit_button)
        self.linear_fit_button.clicked.connect(self.perform_fit)

        ## Plot Button
        self.plot_button = QPushButton('Plot')
        self.button_box_layout.addWidget(self.plot_button)
        self.plot_button.clicked.connect(self.add_plot)

        ## Fit Plot Button
        self.fit_plot_button = QPushButton('Plot Linear Fit')
        self.button_box_layout.addWidget(self.fit_plot_button)
        self.fit_plot_button.clicked.connect(self.add_linear_fit)

        ## Clear Plot Button
        self.clear_button = QPushButton('Clear Plots')
        self.button_box_layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.clear_plot)

        # Axes --------------------------------------------------------
        self.axis_box = QGroupBox()
        self.axis_box_layout = QHBoxLayout(self.axis_box)

        # title box
        self.title_box = QLineEdit()
        self.title_box.setPlaceholderText('plot title')
        self.title_box.textChanged.connect(lambda x: self.label_changed('title', x))
        self.axis_box_layout.addWidget(self.title_box)

        # x axis box
        self.x_box = QLineEdit()
        self.x_box.setPlaceholderText('x label')
        self.x_box.textChanged.connect(lambda x: self.label_changed('x', x))
        self.axis_box_layout.addWidget(self.x_box)

        # y axis box
        self.y_box = QLineEdit()
        self.y_box.setPlaceholderText('y label')
        self.y_box.textChanged.connect(lambda x: self.label_changed('y', x))
        self.axis_box_layout.addWidget(self.y_box)

        self.main_layout.addWidget(self.axis_box, 3, 0, 1, 3)

        ## Main Plotting Widget =======================================
        self.plot_holder = None
        self.main_plot_view = None
        self.main_plot = None
        self.setup_plot()

        # set the line edit
        self.messages_lineEdit = QLineEdit()
        self.messages_lineEdit.setReadOnly(True)
        self.main_layout.addWidget(self.messages_lineEdit, 3, 3, 1, 1)

        ## Menu bar ---------------------------------------------------
        self.file_menu = QMenu('&Actions', self)
        self.file_menu.addAction('&Save Data', self.save_project, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Load Data', self.load_project, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Import CSV', self.import_csv, QtCore.Qt.CTRL + QtCore.Qt.Key_I)
        self.file_menu.addAction('&Fill Data', self.fill_data, QtCore.Qt.CTRL + QtCore.Qt.Key_F)
        self.file_menu.addAction('&Quit', self.close, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        ## Additional Variables ---------------------------------------
        self.linear_fit = None
        self.previous_plot = None
        self.colour_int = 0
        self.fit_colour_int = 0

        self.data_fit_widget = None
        self.data_fill_widgets = []

        #TODO - Remove
        # place holder data
        # for i in range(0, 10):
        #    self.data_table.item(i,0).setText(str(i))
        #    self.data_table.item(i,1).setText(str(i * 2 + 3))
        #    self.data_table.item(i,2).setText('0.2')
        #    self.data_table.item(i,3).setText('0.2')

    def perform_fit(self):
        # get the values we need
        ret_value = self.get_values(errors=False)

        if ret_value is not False:
            # get the specific lists
            x_vals = ret_value[0]
            y_vals = ret_value[1]

            # perform the fit
            slope, intercept, r_squared, p_val, std_error = stats.linregress(x_vals, y_vals)

            self.linear_fit = (slope, intercept)
            self.post('Slope: %s, Intercept: %s, Standard Error %s' % (slope, intercept, std_error))

    def post(self, message):
        self.messages_lineEdit.setText(message)

    def get_values(self, errors=True):
        # values that we wish to return
        x_vals = []
        y_vals = []
        x_errors = []
        y_errors = []
        i = None

        try:
            # get the combo box variables
            x_column = self.dependent_box.currentIndex()
            y_column = self.independent_box.currentIndex()
            x_error_column = self.x_error_box.currentIndex()
            y_error_column = self.y_error_box.currentIndex()

            # get the range (-1 to correct for indexing of displayed rows)
            start = int(self.start_range_box.text()) - 1
            end = int(self.end_range_box.text()) - 1

            # get the values that we care about
            for i in range(start, end):
                x_vals.append(float(self.data_table.item(i, x_column).text()))
                y_vals.append(float(self.data_table.item(i, y_column).text()))

                if errors:
                    x_errors.append(float(self.data_table.item(i, x_error_column).text()))
                    y_errors.append(float(self.data_table.item(i, y_error_column).text()))

            # return the values if we can
            if errors:
                return np.array(x_vals), np.array(y_vals), np.array(x_errors), np.array(y_errors)
            else:
                return np.array(x_vals), np.array(y_vals)

        except ValueError as e:
            if 'base 10' in str(e):
                self.post('Specify both a start and end range.')
            else:
                self.post('Error converting table value to float at row %s' % i)

        # obviously we failed
        return False

    def setup_plot(self):
        # set the plot holder
        self.plot_holder = pg.GraphicsView()

        # set up the main view and set it as the central widget
        self.main_plot_view = pg.GraphicsLayout()
        self.plot_holder.setCentralWidget(self.main_plot_view)

        # add it to the main layout
        self.main_layout.addWidget(self.plot_holder, 0, 3, 3, 1)

        # add an untitled plot
        self.main_plot_view.nextRow()
        self.main_plot = self.main_plot_view.addPlot(1, 1)
        self.main_plot.setTitle('')

    def add_plot(self):
        # get the x and y values
        try:
            x, y, x_errors, y_errors = self.get_values()

            # get the colours
            colour = colours[self.colour_int]

            # get the error bars
            err = pg.ErrorBarItem(x=x, y=y, top=y_errors, bottom=y_errors, left=x_errors, right=x_errors,  beam=0.25,
                                  pen=pg.mkPen(pg.mkColor(colour)))

            # put them both on the plot
            e_plot = self.main_plot.addItem(err)
            plt = self.main_plot.plot(x, y, symbol='o', pen=(0,0,0,0),
                                      symbolBrush=pg.mkBrush(pg.mkColor(colour)),
                                      symbolPen=pg.mkPen(pg.mkColor(colour)))

            # add them to the previous
            self.previous_plot = [e_plot, plt]

            # increment colour
            self.colour_int = (self.colour_int + 1)%3

        except TypeError:
            pass

    def add_linear_fit(self):
        # add the linear fit to the plot if it exists
        if self.linear_fit is not None:
            slope = self.linear_fit[0]
            intercept = self.linear_fit[1]

            # get the points
            x = np.linspace(-1e6, 1e6, 2)
            y = x*slope + intercept

            # get the colour
            colour = colours[self.fit_colour_int]

            # add the slope without it auto resizing
            current_range = self.main_plot.viewRange()
            plt = self.main_plot.plot(x,y,pen=pg.mkPen(color=pg.mkColor(colour + 'AA'), width=1,
                                                       style=QtCore.Qt.DashLine))
            self.main_plot.setXRange(current_range[0][0], current_range[0][1])
            self.main_plot.setYRange(current_range[1][0], current_range[1][1])

            self.previous_plot = [plt]

            # set the linear fit to None
            self.linear_fit = None
            self.fit_colour_int = (self.fit_colour_int + 1)%3
        else:
            self.post('No linear fit loaded.')

    def clear_plot(self):
        # clear all the things
        self.main_plot.clear()
        self.previous_plot = None
        self.colour_int = 0
        self.fit_colour_int = 0

    def label_changed(self, action, text):
        if action == 'title':
            self.main_plot.setTitle(text)
        elif action == 'x':
            self.main_plot.setLabel('bottom', text)
        elif action == 'y':
            self.main_plot.setLabel('left', text)

    def save_project(self):
        name = QFileDialog.getSaveFileName(self, 'Save File', filter="Project Files (*.txt)")

        if name != '':
            # open the file to save data
            try:
                save_file = open(name, 'w+')

                data = []
                # dump the data
                for i in range(self.data_table.rowCount()):
                    for j in range(self.data_table.columnCount()):
                        data.append(str((i,j,str(self.data_table.item(i,j).text()))))

                write_string = '\n'.join(data)

                # write the relevant settings
                save_file.write(write_string)

                # close the file now that we are finished
                save_file.close()
            except IOError:
                msg_box = QMessageBox()
                msg_box.setText('An error occurred trying to save the project. (IOError)')
                msg_box.setWindowTitle('Saving Error')
                msg_box.exec_()

    def load_project(self):
        name = QFileDialog.getOpenFileName(self, "Open File", filter="Project Files (*.txt)")

        if name != '':
            # open the file to save data
            try:
                load_file = open(name, 'r')

                for line in load_file:
                    # get the list out
                    word_list = line.strip('()\n').split(',')
                    word_list = [w.strip(' ').replace("\'", '') for w in word_list]

                    # load into the data table
                    self.data_table.item(int(word_list[0]), int(word_list[1])).setText(word_list[2])

                # close the file now that we are finished
                load_file.close()
            except IOError:
                msg_box = QMessageBox()
                msg_box.setText('An error occurred trying to load the project. (IOError)')
                msg_box.setWindowTitle('Loading Error')
                msg_box.exec_()

    def import_csv(self):
        name = QFileDialog.getOpenFileName(self, "Import File", filter="Data Files (*.csv)")

        if name != '':
            # open the file to save data
            try:
                load_file = open(name, 'r')

                self.data_table.clear()
                self.data_table.setHorizontalHeaderLabels(list(string.ascii_uppercase))
                for i in range(self.table_size[0]):
                    for j in range(self.table_size[1]):
                        self.data_table.setItem(i, j, QTableWidgetItem(''))

                row = 0
                for line in load_file:
                    # get the list out
                    value_list = line.strip().split(',')

                    # load into the data table
                    for v in value_list:
                        self.data_table.item(row, value_list.index(v)).setText(v)

                    row += 1

                # close the file now that we are finished
                load_file.close()
            except IOError:
                msg_box = QMessageBox()
                msg_box.setText('An error occurred trying to import the csv. (IOError)')
                msg_box.setWindowTitle('Loading Error')
                msg_box.exec_()

    def closeEvent(self, event):
        msg_box = QMessageBox()
        msg_box.setText('Are you sure you want to quit?')
        msg_box.setInformativeText('All unsaved changes will be lost.')
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        msg_box.setWindowTitle('Really Exit?')
        ret_val = msg_box.exec_()

        if ret_val == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def fill_data(self):
        # load a dialog for the the fitting of the parameters
        self.data_fit_widget = QDialog()

        # make sure it is modal so it can't be forgotten
        self.data_fit_widget.setModal(True)
        self.data_fit_widget.setFixedSize(260, 250)
        self.setWindowTitle('Fill Column')
        main_layout = QFormLayout(self.data_fit_widget)

        # construct the controls we will use
        # combo box for column selection
        column_combo = QComboBox()
        columns = list(string.ascii_uppercase)[0:self.data_table.columnCount()]
        column_combo.addItems(columns)
        # to box for ending index
        to_box = QLineEdit()
        to_box.setValidator(QIntValidator(1, self.data_table.rowCount()))
        # from box for starting integer
        from_box = QLineEdit()
        from_box.setValidator(QIntValidator(1, self.data_table.rowCount()))
        # value box for the value to set
        val_box = QLineEdit()
        val_box.setValidator(QDoubleValidator())
        # buttons for cancel and submit
        submit_btn = QPushButton('Apply')
        submit_btn.setFixedWidth(150)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.setFixedWidth(150)
        # connect the button actions
        submit_btn.clicked.connect(self.perform_fill)
        cancel_btn.clicked.connect(self.data_fit_widget.close)

        # keep them around for getting the values out later
        self.data_fill_widgets.append(column_combo)
        self.data_fill_widgets.append(to_box)
        self.data_fill_widgets.append(from_box)
        self.data_fill_widgets.append(val_box)

        # add all the controls
        main_layout.addRow('Column:', column_combo)
        main_layout.addRow('From:', from_box)
        main_layout.addRow('To:', to_box)
        main_layout.addRow('Value:', val_box)
        main_layout.addWidget(submit_btn)
        main_layout.addWidget(cancel_btn)

        # finally show the widget
        self.data_fit_widget.show()

    # function used to fill a column
    def perform_fill(self):

        # get out the respective values
        column = self.data_fill_widgets[0].currentIndex()
        from_val = int(self.data_fill_widgets[2].text())
        to_val = int(self.data_fill_widgets[1].text())
        value = self.data_fill_widgets[3].text()

        # loop over the range and set the values
        if from_val > 0 and to_val > 0:
            for i in range(from_val, to_val+1):
                self.data_table.item(i-1, column).setText(value)
        else:
            self.messages_lineEdit.setText('From and To values must be greater than 0.')

        # clear everything
        self.data_fill_widgets = []
        self.data_fit_widget.close()