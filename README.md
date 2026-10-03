# Weather Report CI/CD Pipeline (Capstone Project)

A small end-to-end DevOps project. A Python script reports the weather for **any city in the world**. The code lives in GitHub, **Jenkins** runs it on demand, **Ansible** delivers a **Splunk-generated report** to a QA server, and a dedicated **10G filesystem** hosts the cloned repository.

> **Notes**
> - **GitHub** is used as the central repository (the assignment text mentions GitLab).
> - The repository is named `weather_report`.
> - The dedicated 10G `weather_report` filesystem is on **`qaserver`**.

---

## Table of contents

1. [Architecture](#architecture)
2. [Environment](#environment)
3. [Question 1: Architect plan](#question-1-architect-plan)
4. [Question 2: 10G filesystem and repository](#question-2-10g-filesystem-and-repository)
5. [Question 3: Splunk, report, Ansible and Jenkins](#question-3-splunk-report-ansible-and-jenkins)
6. [The weather script](#the-weather-script)
7. [Question 4: Incident response plan](#question-4-incident-response-plan)
8. [Problems I faced and how I fixed them](#problems-i-faced-and-how-i-fixed-them)
9. [Final result](#final-result)
10. [Screenshot checklist](#screenshot-checklist)

---

## Architecture

![Architecture diagram](screenshots/architecture.png)

*The person pushes code to GitHub (SCM). A Jenkins build, started with the `CITY` and `REGION` parameters, checks the code out on the `automation` VM, runs `weather_report.py` (which calls the Open-Meteo weather API) and then the Ansible playbook, which copies `Final.report.CSV` to `/tmp` on `qaserver`. The repository is cloned into the 10G `/weather_report` filesystem on `qaserver`. Splunk (also on `automation`) produces `Final.report.CSV`, which is committed to GitHub. Jenkins shows the results in its console output.*

**Repository contents**

| File | Purpose |
|---|---|
| `architecture.png` | Architecture diagram shown above |
| `weather_report.py` | Prints the weather for any city, with its local time |
| `Final.report.CSV` | Report exported from the Splunk index `weather_index_report` |
| `copy_report.yml` | Ansible playbook that copies `Final.report.CSV` to `/tmp` on `qaserver` |
| `Incident_Response_Plan.pptx` | 3-slide incident response presentation (Question 4) |

---

## Environment

| Item | Value |
|---|---|
| Virtualization | Oracle VM VirtualBox |
| `automation` | Linux VM running Jenkins, Ansible and Splunk |
| `qaserver` | Linux VM (Ubuntu), the target server; hosts the 10G `weather_report` filesystem |
| Source control | GitHub: `https://github.com/cool129/weather_report` |
| Automation | Jenkins (Freestyle job `weather_report2`) and Ansible |
| Editor | VS Code on Windows (Git Bash terminal), WinSCP for file transfer |

---

## Question 1: Architect plan

Requirements: host the weather monitoring software on a virtual server, keep the script in a central repository (CI/CD concept), and run it daily with a suitable automation tool.

1. **Provision the servers.** Two Linux virtual servers in VirtualBox: `automation` (Jenkins, Ansible, Splunk) and `qaserver` (the QA target).
2. **Create the dedicated filesystem.** Attach a 10G virtual disk to `qaserver`, format it as ext4, mount it at `/weather_report`, and make the mount permanent in `/etc/fstab`.
3. **Set up the central repository.** Create the GitHub repository and push the script, the playbook and the report.
4. **Clone the repository** into the `/weather_report` filesystem on `qaserver`.
5. **Ingest and report in Splunk.** Create the `weather_index_report` index, ingest the dataset, run the search and export `Final.report.CSV`.
6. **Prepare Ansible.** Add `qaserver` to the inventory and write `copy_report.yml`.
7. **Automate with Jenkins.** A Freestyle job pulls the code from GitHub, runs the weather script and runs the playbook. Jenkins is the automation tool, so an intern can run it with one click (or on a schedule).
8. **Verify end to end.** The build ends in `Finished: SUCCESS` and the file exists in `/tmp` on `qaserver`.

---

## Question 2: 10G filesystem and repository

### 2.1 Attach and identify the disk

A 10G virtual disk was attached to `qaserver`. `lsblk` shows it as `sdc` with no mount point.

![lsblk showing the 10G sdc disk](screenshots/01-lsblk-disks.png)

### 2.2 Format and mount at `/weather_report`

```bash
sudo blkid /dev/sdc                      # check whether it already has a filesystem
sudo mkfs.ext4 -L weather_report /dev/sdc   # only if blkid printed nothing
sudo mkdir -p /weather_report
sudo mount /dev/sdc /weather_report
sudo chown geo2face:geo2face /weather_report
df -h /weather_report
