import sys
import re
import csv
import os
import json
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QListWidget, QMessageBox, QLineEdit, QInputDialog, QVBoxLayout, QWidget, QCheckBox
from PyQt5.QtCore import Qt


class EmailPasswordChecker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Combolist Checker")
        self.setGeometry(100, 100, 600, 400)
        self.research_specific_enabled = False
        self.hystory_file = 'storico.json'

        self.domains_sets = {
            "Client1": 
                ["client1.com", "client1.org"],
                            
            "Client2": 
                ["client2.com", "client2.org"],
    
            "Client3":
                ["client3.com", "client3.org"],

            [...]
        }

        self.history = self.upload_history()

        self.listbox = QListWidget(self)

        self.btn_open = QPushButton("Open File", self)
        self.btn_open.clicked.connect(self.apri_file)
        
        self.chk_research_specific = QCheckBox("Specific Search", self)
        self.chk_research_specific.stateChanged.connect(self.toggle_specific_search)

        self.domains_label = QLabel(Select domains set:", self)

        layout = QVBoxLayout()
        layout.addWidget(self.listbox)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.chk_research_specific)
        layout.addWidget(self.domains_label)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.domains_checkboxes = {}
        for dominio in self.domains_sets.keys():
            checkbox = QCheckBox(domain, self)
            layout.addWidget(checkbox)
            self.domains_checkboxes[domain] = checkbox
        
    def toggle_specific_search(self, state):
        self.specific_search_enabled = (state == Qt.Checked)
            
    def upload_history(self):
        if os.path.exists(self.file_history):
            with open(self.file_history, 'r') as file:
                return json.load(file)
        else:
            return []

    def save_history(self):
        with open(self.file_history, 'w') as file:
            json.dump(self.history, file)

    def get_specific_email(self):
        searched_email, ok = QInputDialog.getText(self, Specific search", "Inserisci l'email da cercare:")
        if ok:
            return searched_email
        return None
        
    def open_file(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select File", "", "Text Files (*.txt)")
        
        if not filenames:
            return

        output_folder = QFileDialog.getExistingDirectory(self, "Select output folder")
        if not output_folder:
            return

        base_name = os.path.basename(filenames[0])
        name, ext = os.path.splitext(base_name)
        first_date = name.split('_')[-1]
        csv_file_path = os.path.join(output_folder, f'output_{first_date}.csv')

        selected_domains = [domain for domain, checkbox in self.domains_checkboxes.items() if checkbox.isChecked()]
        if not selected_domains and not self.specific_search_enabled:
            QMessageBox.warning(self, "Error", "Select one domain set.")
            return
            
        searched_email = None
        if self.research_specific_enabled:
            searched_email = self.get_specific_email()
            if searched_email is None:
                return
        
        for filename in filenames:
            if filename and filename not in self.history:
                self.history.append(filename)
                self.save_history()
                self.listbox.addItem(filename)

            base_name = os.path.basename(filename)
            name, ext = os.path.splitext(base_name)
            selected_date = name.split('_')[-1]

            try:
                selected_date = datetime.strptime(selected_date, '%d-%m-%y').strftime('%Y-%m-%d')
            except ValueError:
                selected_date = "Date not valid"
            
            if self.specific_search_enabled:
                self.process_file(filename, selected_date, "Specific search", csv_file_path, searched_email)
            else:
                for domain in selected_domains:
                    print(f"search for {filename}")
                    self.process_file(filename, selected_date, domain, csv_file_path, searched_email)
                    
        self.remove_duplicates(csv_file_path)

    def process_file(self, filename=None, selected_date=None, domain_set=None, csv_file_path=None, searched_email=None):
        if not filename or not selected_date or not domain_set or not csv_file_path:
            return

        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        combolist = os.path.splitext(os.path.basename(filename))[0]
        combolist = combolist.rsplit('_', 1)[0]

        found = False
        try:
            with open(csv_file_path, 'a+', newline='') as csv_file:
                writer = csv.writer(csv_file)

                csv_file.seek(0)

                if csv_file.read() == '':
                    writer.writerow(["Email", "Password", "Email_Password", "URL", "Source date", "Data Leak", "TAG"])

                csv_file.seek(0, os.SEEK_END)

                for line in lines:
                    match = re.search(r'(https?://[^:]+)?:?(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b):(\w+)', line)
                    if match:
                        url = match.group(1) or ''
                        email = match.group(2)
                        password = match.group(3)
                        email_password = email + ':' + password
                        domain = email.split('@')[1]

                        if self.specific_search_enabled:
                            if searched_email and email == searched_email:
                                writer.writerow([email, password, email_password, url, selected_date, combolist, domain_set])
                                found = True
                        else:
                            if domain in self.domains_sets[domain_set]:
                                writer.writerow([email, password, email_password, url, selected_date, combolist, domain_set])
                                found = True                      

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error in the creation of the CSV file:\n{e}")

        if found:
            print(f"Completed, findings saved in {csv_file_path}")
        else:
            print("Nothing found")

    def remove_duplicates(self, csv_file_path):
        df = pd.read_csv(csv_file_path)

        df.sort_values('Source date', inplace=True)

        df.drop_duplicates(subset='Email_Password', keep='first', inplace=True)

        df.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailPasswordChecker()
    window.show()
    sys.exit(app.exec_())

