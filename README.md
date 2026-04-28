# Test repo for Regis =)

## Overview

This project implements an Ansible-based solution to:

- Detect configuration drift
- Remediate non-compliant configuration files
- Capture configuration state before and after remediation
- Generate a structured JSON execution report with per-file drift information
- Track changed tasks, failed tasks, and unreachable hosts

The solution uses only idempotent Ansible modules and a custom callback plugin for execution reporting.

---

# Managed Configuration

The solution supports management of multiple configuration files through a data-driven structure defined in:

```text
regisapp/defaults/main.yml
```

or optionally overridden in:

```text
regisapp/vars/main.yml
```

Example:

```yaml
app_configs:
  - name: app.conf
    path: /etc/demo-app/app.conf
    template: app.conf.j2
    config:
      port: 8443
      ssl: true
      log_level: info
```

Expected managed configuration content:

```text
port=8443
ssl=true
log_level=info
```

Additional configuration files can be added without modifying the role logic.

---

# Assumptions

The following assumptions were made during implementation:

- The application runs under a dedicated system user named `regisapp`
- The application group is also `regisapp`
- Configuration files are fully managed by Ansible
- Missing configuration files are considered configuration drift
- Configuration directories may not exist and should be created automatically
- Target systems are Linux-based servers
- Configuration files may contain sensitive information, therefore restrictive permissions are applied
- Reports are generated locally under the `reports/` directory
- The Ansible controller is responsible for generating the execution reports

---

# Security Considerations

Managed configuration files are created with restricted permissions:

```text
0640
```

Configuration directories are created with:

```text
0750
```

This limits configuration access to the application user and group.

---

# Idempotency

The solution uses only idempotent Ansible modules:

- `template`
- `file`
- `group`
- `user`
- `stat`
- `slurp`
- `set_fact`

Repeated executions will not generate unnecessary changes when configurations are already compliant.

---

# Configuration Drift Detection

Configuration drift is detected by:

1. Reading the existing configuration file using `slurp`
2. Capturing the configuration content before remediation
3. Applying the expected configuration using a Jinja2 template
4. Reading the configuration again after remediation
5. Comparing the before and after content

If differences are detected, the configuration is automatically remediated.

---

# Callback Plugin

A custom callback plugin is used to:

- Capture changed tasks
- Capture failed tasks
- Capture unreachable hosts
- Generate a structured JSON report
- Store configuration before/after values
- Support multiple managed configuration files

The plugin writes execution reports to:

```text
reports/report_20260428_190602Z.json
```

Reports are timestamped using UTC time to ensure consistency across environments and CI/CD systems.

---

# Variables

Default variables are defined under:

```text
regisapp/defaults/main.yml
```

Example:

```yaml
app_user: regisapp
app_group: regisapp

app_configs:
  - name: app.conf
    path: /etc/demo-app/app.conf
    template: app.conf.j2
    config:
      port: 8443
      ssl: true
      log_level: info

app_dir_mode: '0750'
app_file_mode: '0640'

app_create_user: true
```

---

# Template

Managed configuration templates are stored under:

```text
regisapp/templates/
```

Example template:

```text
regisapp/templates/app.conf.j2
```

Content:

```jinja2
port={{ app_config.config.port }}
ssl={{ app_config.config.ssl | lower }}
log_level={{ app_config.config.log_level | lower }}
```

---

# Inventory Example

```ini
[servers]
server01 ansible_host=192.168.1.10 ansible_user=ec2-user
```

---

# Playbook Execution

Execute the playbook with:

```bash
ANSIBLE_CALLBACKS_ENABLED=custom_json_report ansible-playbook -i inventory.ini site.yml -K
```

Where:

- `-K` prompts for the sudo password
- `ANSIBLE_CALLBACKS_ENABLED` enables the custom callback plugin

---

# Example JSON Report

```json
{
  "started_at": "2026-04-27T15:00:00Z",
  "finished_at": "2026-04-27T15:01:00Z",
  "changed": [
    {
      "host": "server01",
      "task": "Ensure application configuration is compliant",
      "config_file": "/etc/demo-app/app.conf",
      "status": "changed",
      "before": "port=8080\nssl=false\nlog_level=debug",
      "after": "port=8443\nssl=true\nlog_level=info"
    }
  ],
  "failed": [],
  "unreachable": []
}
```

---

# Error Handling

The solution captures:

- Task failures
- Unreachable hosts
- Configuration drift state
- Per-file remediation information

All execution data is centralized in the generated JSON report.

---

# Bonus Features

Implemented bonus enhancements include:

- Support for multiple configuration files
- Timestamped execution reports
- Per-file drift reporting
- CI/CD-friendly JSON output structure

---

# Author

Esteban Monge
