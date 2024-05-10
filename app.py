from flask import Flask, render_template, request, redirect, url_for
import subprocess
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

# Function to check if antivirus is active
def check_antivirus():
    try:
        # Using Windows Security Center to check antivirus status
        result = subprocess.check_output(['wmic', '/namespace:\\\\root\\SecurityCenter2', 'path', 'AntiVirusProduct', 'get', 'displayName'], stderr=subprocess.STDOUT, universal_newlines=True)
        if "displayName" in result:
            return "Passed: Antivirus software is installed."
        else:
            return "Failed: Antivirus software is not detected."
    except subprocess.CalledProcessError as e:
        return "Failed to check antivirus status. Error: " + str(e)

# Function to check if Windows Firewall is enabled
def check_firewall():
    try:
        # Using netsh command to check firewall status
        result = subprocess.check_output(['netsh', 'advfirewall', 'show', 'allprofiles'], stderr=subprocess.STDOUT, universal_newlines=True)
        if "State ON" in result:
            return "Passed: Windows Firewall is enabled."
        else:
            return "Failed: Windows Firewall is disabled."
    except subprocess.CalledProcessError as e:
        return "Failed to check firewall status. Error: " + str(e)

# Function to check if automatic updates are enabled
def check_updates():
    try:
        # Using Windows Update service status to check for automatic updates
        result = subprocess.check_output(['sc', 'query', 'wuauserv'], stderr=subprocess.STDOUT, universal_newlines=True)
        if "RUNNING" in result:
            return "Passed: Automatic updates are enabled."
        else:
            return "Failed: Automatic updates are disabled."
    except subprocess.CalledProcessError as e:
        return "Failed to check updates status. Error: " + str(e)

# Function to generate and print the report
def generate_report():
    report = []
    report.append(check_antivirus())
    report.append(check_firewall())
    report.append(check_updates())

    report_str = "\n".join(report)
    return report_str

# Run the checks and generate the report
report = generate_report()

# Print the report
print("Security Checklist Report:")
print(report)


def log_report_to_firestore(report_lines):
    doc_ref = db.collection('reports').document()
    doc_ref.set({"lines": report_lines})

def generate_report():
    report = []
    report.append(check_antivirus())
    report.append(check_firewall())
    report.append(check_updates())

    # Log to Firestore
    log_report_to_firestore(report)

    report_str = "\n".join(report)
    return report_str

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        report = generate_report()
        report_lines = report.split('\n')
    else:
        report_lines = []
    return render_template('index.html', report_lines=report_lines)

if __name__ == '__main__':
    app.run(debug=True)