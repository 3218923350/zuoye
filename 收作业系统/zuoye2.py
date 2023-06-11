# -*- code = utf-8 -*-
# @Time : 2023/6/11 16:27
# @Author : 王毅
# @File : zuoye2.py
# @Software : PyCharm
import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, \
    QLineEdit, QFileDialog, QTextEdit, QMessageBox
from PyQt5.QtCore import QDir
import pandas as pd
import shutil


def get_path():
    return os.getcwd()


def split_string(string, pattern):
    return string.split(pattern)


def process_files(path, student_file_path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_list.append(file)

    missing_students = []
    if student_file_path.endswith('.txt'):
        with open(student_file_path, 'r') as infile:
            lines = infile.readlines()
            for line in lines:
                temp = line.strip().split('\t')
                exist = False
                for file in file_list:
                    if temp[0] in file or temp[1] in file:
                        exist = True
                        file_list.remove(file)
                        break
                if not exist:
                    missing_students.append((temp[0], temp[1]))
    elif student_file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(student_file_path)
        for _, row in df.iterrows():
            temp = [str(cell) for cell in row]
            exist = False
            for file in file_list:
                if temp[0] in file or temp[1] in file:
                    exist = True
                    file_list.remove(file)
                    break
            if not exist:
                missing_students.append((temp[1], temp[2]))

    return missing_students


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("未交查询")

        # 创建标签和输入框
        label_path = QLabel("路径：", self)
        self.lineEdit_path = QLineEdit(self)
        button_browse = QPushButton("浏览", self)

        # 创建标签和输入框
        label_student_file = QLabel("学生文件：", self)
        self.lineEdit_student_file = QLineEdit(self)
        button_student_file = QPushButton("选择文件", self)

        # 创建按钮
        button_search = QPushButton("查询", self)

        # 创建文本框
        self.text_edit_output = QTextEdit(self)
        self.text_edit_output.setReadOnly(True)

        # 布局管理器
        h_layout_path = QHBoxLayout()
        h_layout_path.addWidget(label_path)
        h_layout_path.addWidget(self.lineEdit_path)
        h_layout_path.addWidget(button_browse)

        h_layout_student_file = QHBoxLayout()
        h_layout_student_file.addWidget(label_student_file)
        h_layout_student_file.addWidget(self.lineEdit_student_file)
        h_layout_student_file.addWidget(button_student_file)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout_path)
        v_layout.addLayout(h_layout_student_file)
        v_layout.addWidget(button_search)
        v_layout.addWidget(self.text_edit_output)

        central_widget = QWidget(self)
        central_widget.setLayout(v_layout)
        self.setCentralWidget(central_widget)

        # 连接按钮点击事件
        button_browse.clicked.connect(self.browse_directory)
        button_student_file.clicked.connect(self.select_student_file)
        button_search.clicked.connect(self.search_files)

        # 默认学生文件路径
        self.default_student_file_path = None

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", QDir.homePath(), QFileDialog.ShowDirsOnly)
        self.lineEdit_path.setText(directory)

    # def select_student_file(self):
    #     if self.default_student_file_path is None:
    #         default_dir = QDir.homePath()
    #     else:
    #         default_dir = os.path.dirname(self.default_student_file_path)
    #
    #     student_file_path, _ = QFileDialog.getOpenFileName(self, "选择学生文件", default_dir, "Text Files (*.txt);;Excel Files (*.xls *.xlsx)")
    #     if student_file_path:
    #         self.lineEdit_student_file.setText(student_file_path)
    #         self.default_student_file_path = student_file_path
    def select_student_file(self):
        if self.default_student_file_path is not None:
            default_dir = os.path.dirname(self.default_student_file_path)
        else:
            default_dir = QDir.homePath()

        student_file_path, _ = QFileDialog.getOpenFileName(self, "选择学生文件", default_dir,
                                                           "Text Files (*.txt);;Excel Files (*.xls *.xlsx)")
        if student_file_path:
            self.lineEdit_student_file.setText(student_file_path)
            self.default_student_file_path = student_file_path

    def search_files(self):
        path = self.lineEdit_path.text()
        student_file_path = self.lineEdit_student_file.text()
        if not student_file_path and self.default_student_file_path:
            student_file_path = self.default_student_file_path

        missing_students = process_files(path, student_file_path)
        if missing_students:
            output = ""
            for student in missing_students:
                output += f"学号: {student[0]}\t姓名: {student[1]}\n"
            self.text_edit_output.setText(output)
            self.text_edit_output.selectAll()
            self.text_edit_output.setFocus()
            QMessageBox.information(self, "未交作业的学生", "以下是未交作业的学生姓名和学号")

            # 保存学生文件到当前路径
            if student_file_path.endswith(('.txt', '.xls', '.xlsx')):
                file_name = os.path.basename(student_file_path)
                save_path = os.path.join(get_path(), file_name)
                shutil.copy2(student_file_path, save_path)
                self.default_student_file_path = save_path


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
