from ansible.plugins.callback import CallbackBase
from datetime import datetime
import json
import os

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'custom_json_report'

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.report = {
            "started_at": None,
            "finished_at": None,
            "changed": [],
            "failed": [],
            "unreachable": []
        }

    def v2_playbook_on_start(self, playbook):
        self.report["started_at"] = datetime.utcnow().isoformat() + "Z"

    def v2_runner_on_ok(self, result):
        result_data = result._result

        if "ansible_facts" not in result_data:
            return

        facts = result_data["ansible_facts"]

        if "app_conf_report" not in facts:
            return

        report = facts["app_conf_report"]

        if report["drifted"]:

            self.report["changed"].append({
                "host": report["host"],
                "task": report["task"],
                "status": "changed",
                "config_file": report["config_file"],
                "before": report["before"],
                "after": report["after"]
            })

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        task_name = result.task_name

        self.report["failed"].append({
            "host": host,
            "task": task_name,
            "status": "failed"
        })

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()

        self.report["unreachable"].append({
            "host": host,
            "status": "unreachable"
        })

    def v2_playbook_on_stats(self, stats):
        self.report["finished_at"] = datetime.utcnow().isoformat() + "Z"

        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = f"reports/report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(self.report, f, indent=2)
