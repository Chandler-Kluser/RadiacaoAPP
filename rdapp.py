import sys
from PyQt5 import QtWidgets
import mainwindow
from numpy import savetxt
from radiacaoapp import *

def InitializeApplication():
    global cpl_list,showMessage
    showMessage=False
    # mark true when the nonlinear feature be working
    ui.cpl_nonlin_combobox.setEnabled(False)
    ui.cpl_nonlin_text.setEnabled(False)

    cpl_list = []
    ui.res_but.clicked.connect(res_but_clicked)
    ui.cpl_but.clicked.connect(cpl_but_clicked)
    ui.view_but.clicked.connect(view_but_clicked)
    ui.radsurf_but.clicked.connect(radsurf_but_clicked)
    ui.load_but.clicked.connect(load_but_clicked)
    ui.submit_radsurf_but.clicked.connect(submit_radsurf_but_clicked)
    ui.create_view_but.clicked.connect(create_view_but_clicked)
    ui.clear_all_views_but.clicked.connect(clear_all_views_but_clicked)
    ui.create_cpl_but.clicked.connect(create_cpl_but_clicked)
    ui.cpl_radsurf_add_but.clicked.connect(cpl_radsurf_add_but_clicked)
    ui.cpl_radsurf_clear_but.clicked.connect(cpl_radsurf_clear_but_clicked)
    ui.cpl_radsurf_list_but.clicked.connect(cpl_radsurf_list_but_clicked)
    ui.create_load_but.clicked.connect(create_load_but_clicked)
    ui.clear_all_load_but.clicked.connect(clear_all_load_but_clicked)
    ui.clear_all_but.clicked.connect(clear_all_but_clicked)
    ui.save_ls_but.clicked.connect(save_ls_but_clicked)
    ui.solve_but.clicked.connect(solve_but_clicked)

def radsurf_but_clicked():
    ui.stackedWidget.setCurrentIndex(0)

def view_but_clicked():
    ui.stackedWidget.setCurrentIndex(1)
    # update comboboxes
    ui.view_departure_radsurf_combobox.clear()
    ui.view_arrival_radsurf_combobox.clear()
    for i in radsurf.list:
        ui.view_departure_radsurf_combobox.addItem(str(i.num))
        ui.view_arrival_radsurf_combobox.addItem(str(i.num))

def cpl_but_clicked():
    ui.stackedWidget.setCurrentIndex(2)
    # update comboboxes
    ui.cpl_radsurf_add_combobox.clear()
    for i in radsurf.list:
        ui.cpl_radsurf_add_combobox.addItem(str(i.num))
    
def load_but_clicked():
    ui.stackedWidget.setCurrentIndex(3)
    # update comboboxes
    ui.load_radsurf_combobox.clear()
    for i in radsurf.list:
        ui.load_radsurf_combobox.addItem(str(i.num))

def res_but_clicked():
    ui.stackedWidget.setCurrentIndex(4)
    ui.progressBar.setProperty("value",0)

def show_error(error_message):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    msgBox.setWindowTitle("Error")
    msgBox.setText(error_message)
    msgBox.exec()

def show_message(message):
    global showMessage
    if showMessage:
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setWindowTitle("Message")
        msgBox.setText(message)
        msgBox.exec()

def submit_radsurf_but_clicked():
    try:
        emissivity = float(ui.emissivity_text.text())
        area = float(ui.area_text.text())
        try:
            if emissivity<=0 or emissivity>1:
                raise Exception("Emissivity must be positive and less or equal to 1.")
            elif area<=0:
                raise Exception("Area must be greater than 0.")
            else:
                radsurf(emissivity, area)
                show_message("Radiant Surface Created!")
        except Exception as msg:
            show_error(msg.args[0])
    except:
        show_error("Parameters not Valid.")

def create_view_but_clicked():
    try:
        num_radsurf_depart = int(ui.view_departure_radsurf_combobox.currentText())
        num_radsurf_arrival = int(ui.view_arrival_radsurf_combobox.currentText())
        ViewFactor = float(ui.view_viewfactor_text.text())
        try:
            ok = True
            for i in view.list:
                if ok:
                    if (i.dep.num==num_radsurf_depart and i.arr.num==num_radsurf_arrival) or (i.arr.num==num_radsurf_depart and i.dep.num==num_radsurf_arrival):
                        ok=False
            if not ok:
                raise Exception("There is already a View with these two Radiant Surfaces submitted.")
            elif num_radsurf_depart==num_radsurf_arrival:
                raise Exception("Departure and Arrival Radiant Surfaces must not be the same.")
            elif ViewFactor<=0 or ViewFactor>1:
                raise Exception("View Factor must be greater than 0 and less or equal to 1.")
            else:
                view(num_radsurf_depart,num_radsurf_arrival,ViewFactor)
                show_message("View Created!")
        except Exception as msg:
            show_error(msg.args[0])
    except:
        show_error("Parameters not Valid.")

def clear_all_views_but_clicked():
    view.clear()
    show_message("Views Cleared!")

def cpl_radsurf_add_but_clicked():
    global cpl_list
    try:
        idx = int(ui.cpl_radsurf_add_combobox.currentText())
        ok = True
        for i in cpl.list:
            if ok:
                for j in i.radsurf_list:
                    if idx==j.num:
                        ok=False
        ok2 = True
        for i in cpl_list:
            if ok2:
                if i==idx:
                    ok2=False
        try:
            if not ok:
                raise Exception("This Radiant Surface already belongs to another coupling")
            elif not ok2:
                raise Exception("This Radiant Surface is already selected for the actual coupling.")
            else:
                cpl_list.append(idx)
                show_message("Surface Added to Coupling!")
        except Exception as msg:
            show_error(msg.args[0])
    except:
        show_error("Radiant Surface not Valid.")

def create_cpl_but_clicked():
    global cpl_list
    try:
        q_gen1 = float(ui.cpl_egen_text.text())
        try:
            if len(cpl_list)<=1:
                raise Exception("The coupling must have at least 2 Radiant Surfaces")
            else:
                cpl(cpl_list,q_gen1)
                cpl_list=[]
        except Exception as msg:
            show_error(msg.args[0])
    except:
        show_error("Please enter a valid Energy Generation ratio.")

def cpl_radsurf_clear_but_clicked():
    global cpl_list
    cpl_list = []
    show_message("Surfaces Added were Cleared in current Coupling.")

def cpl_radsurf_list_but_clicked():
    global cpl_list
    # TO DO:
    # MAKE A DEDICATED WINDOW WITH A TABLE TO LIST THE SURFACES
    listed = ""
    first = True
    for i in cpl_list:
        if first:
            listed += str(i)
            first = False
        else:
            listed += "\n"+str(i)
    if cpl_list==[]:
        show_error("No Surfaces Added.")
    else:
        show_error(listed)

def create_load_but_clicked():
    try:
        num = int(ui.load_radsurf_combobox.currentText())
        value = float(ui.load_val_text.text())
        type_num = int(ui.load_type_combobox.currentIndex())
        ok = True
        for i in load.list:
            if ok:
                if (i.radsurf.num==num) and (i.type==type_num):
                    ok=False
        try:
            if ok==False:
                raise Exception("There is already a load of this type submitted to this Radiant Surface.")
            elif type_num==0 and value<0:
                raise Exception("Temperature must be greater than 0.")
            elif type_num==2 and value<0:
                raise Exception("Radiosity must be greater than 0.")
            else:
                load(num,value,type_num)
                show_message("Load Created!")
        except Exception as msg:
            show_error(msg.args[0])
    except:
        show_error("Invalid entry.")

def clear_all_load_but_clicked():
    load.clear()
    show_message("All Loads Cleared!")

def clear_all_but_clicked():
    global cpl_list
    view.clear()
    cpl.clear()
    cpl_list=[]
    radsurf.list = []
    radsurf.total = 0
    show_message("All Entities Cleared!")

def save_ls_but_clicked():
    A,B,n = mount()
    savetxt("A.csv",A,fmt='%.4f',delimiter=',')
    # savetxt("A.csv",A,delimiter=',')
    savetxt("B.csv",B,fmt='%.4f',delimiter=',')
    # savetxt("B.csv",B,delimiter=',')
    show_message("Linear System Files Saved!")

def solve_but_clicked():
    try:
        ui.progressBar.setProperty("value",0)
        A,B,n = mount()
        ui.progressBar.setProperty("value",25)
        A,B,X,Xt = solve()
        ui.progressBar.setProperty("value",90)
        savetxt("X_EmisssivePowers.csv",X,fmt='%.4f',delimiter=',')
        ui.progressBar.setProperty("value",95)
        savetxt("X_Temperatures.csv",Xt,fmt='%.4f',delimiter=',')
        ui.progressBar.setProperty("value",100)
        show_message("Linear System Files Saved!")
    except Exception as msg:
        show_error(msg.args[0])

app = QtWidgets.QApplication(sys.argv)
RadiacaoAPP = QtWidgets.QMainWindow()
ui = mainwindow.Ui_RadiacaoAPP()
ui.setupUi(RadiacaoAPP)

# Initialize app at screen center
qtRectangle = RadiacaoAPP.frameGeometry()
centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
qtRectangle.moveCenter(centerPoint)
RadiacaoAPP.move(qtRectangle.topLeft())
# show app
RadiacaoAPP.show()

# initialize app
InitializeApplication()

sys.exit(app.exec_())