"""Contract smoke tests for the PD inference compute API."""
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "orchestrator_service"))

from adapters.compute.sdk.job import JobClient  # noqa: E402
from adapters.compute.sdk.monitor import MonitorClient  # noqa: E402
from main import app  # noqa: E402


class PDComputeApiTests(unittest.TestCase):
    def setUp(self):
        self.jobs = JobClient()

    def test_pd_job_lifecycle(self):
        submitted = self.jobs.submit_pd_infer_job(
            "prefill-test", "ShenZhen-DC-C", "default", "default",
            role="Prefill",
        )
        self.assertEqual(200, submitted["respCode"])
        self.assertEqual("Prefill", submitted["respBody"]["role"])
        job_id = submitted["respBody"]["jobId"]

        detail = self.jobs.get_pd_job_detail(job_id)
        self.assertEqual("PDinfer", detail["respBody"]["taskjob_type"])
        self.assertEqual(200, self.jobs.query_pd_job_time_limit(job_id)["respCode"])
        self.assertEqual(200, self.jobs.change_pd_job_time_limit(job_id, 5)["respCode"])
        self.assertEqual(200, self.jobs.cancel_pd_job(job_id)["respCode"])

    def test_proxy_requires_pd_addresses(self):
        with self.assertRaises(ValueError):
            self.jobs.submit_pd_infer_job(
                "proxy-test", "GuangZhou-DC-B", "default", "default",
                role="Proxy",
            )

    def test_pd_metrics_names(self):
        metrics = MonitorClient().get_job_metrics(1)["respBody"]["metrics"]
        self.assertIn("ttft", {item["metric_types"] for item in metrics})
        self.assertIn("tpot", {item["metric_types"] for item in metrics})

    def test_documented_routes_are_registered(self):
        paths = {route.path for route in app.routes}
        expected = {
            "/api/v1/compute/adapter/pdinferjobs",
            "/api/v1/compute/adapter/getSpecPDJob",
            "/api/v1/compute/adapter/CancelSpecPDJob",
            "/api/v1/compute/adapter/queryPDJobTimeLimit",
            "/api/v1/compute/adapter/changePDJobTimeLimit",
            "/api/v1/compute/adapter/getPDJobMonitorMetrics",
            "/api/v1/compute/notification/stream",
            "/api/v1/compute/notification/webhook/unsubscribe",
            "/api/v1/compute/inference/chat/completions",
        }
        self.assertFalse(expected - paths)


if __name__ == "__main__":
    unittest.main()
