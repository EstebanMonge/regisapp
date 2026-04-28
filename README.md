# Test repo for Regis =)

## Overview

This project implements an Ansible-based solution to:

- Detect configuration drift
- Remediate non-compliant configuration files
- Capture configuration state before and after remediation
- Generate a structured JSON execution report
- Track changed tasks, failed tasks, and unreachable hosts

The solution uses only idempotent Ansible modules and a custom callback plugin for execution reporting.

---

# Managed Configuration

The following configuration file is managed:

```text
/etc/demo-app/app.conf
```

Expected content:

```text
port=8443
ssl=true
log_level=info
```

---

# Assumptions

The following assumptions were made during implementation:

- The application runs under a dedicated system user named `regisapp`
- The application group is also `regisapp`
- The configuration file is fully managed by Ansible
- Missing configuration files are considered configuration drift
- The configuration directory may not exist and should be created automatically
- Target systems are Linux-based servers
- The configuration file may contain sensitive information, therefore restrictive permissions are applied
- Reports are generated locally under the `reports/` directory

---

# Security Considerations

The managed configuration file is created with restricted permissions:

```text
0640
```

The configuration directory is created with:

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

Repeated executions will not generate unnecessary changes when the configuration is already compliant.

---

# Configuration Drift Detection

Configuration drift is detected by:

1. Reading the existing configuration file using `slurp`
2. Capturing the configuration content before remediation
3. Applying the expected configuration using a Jinja2 template
4. Reading the configuration again after remediation
5. Comparing the before and after content

---

# Callback Plugin

A custom callback plugin is used to:

- Capture changed tasks
- Capture failed tasks
- Capture unreachable hosts
- Generate a structured JSON report
- Store configuration before/after values

The plugin writes the execution report to:

```text
reports/report.json
```

---

# Variables

Default variables are defined under:

```text
regisapp/defaults/main.yml
```

Example:

```yaml
app_user: regisapp
app_group: "{{ app_user }}"
app_config_dir: /etc/demo-app
app_config_path: /etc/demo-app/app.conf
app_dir_mode: '0750'
app_file_mode: '0640'
app_create_user: false
```

---

# Template

The managed configuration template:

```text
regisapp/templates/app.conf.j2
```

Content:

```jinja2
port={{ app_port }}
ssl={{ app_ssl | lower }}
log_level={{ app_log_level }}
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

All execution data is centralized in the generated JSON report.

---

# Author

Esteban Monge


