import os
import mock
import unittest
import requests_mock
import requests
from requests.auth import HTTPBasicAuth
from tenacity import stop_after_delay, stop_after_attempt
from pipeline_tools import get_analysis_metadata


class TestGetAnalysisMetadata(unittest.TestCase):

    def setUp(self):
        self.workflow_id = 'id'
        self.runtime_environment = 'dev'
        base_url = 'https://cromwell.mint-{}.broadinstitute.org/api/workflows/v1'.format(self.runtime_environment)
        self.cromwell_url = '{}/{}/metadata?expandSubWorkflows=true'.format(base_url, self.workflow_id)

    @unittest.skip('Skipping until get_worflow_id correctly parses the analysis subworkflow id')
    def test_get_workflow_id(self):
        analysis_output_path = 'gs://broad-dsde-mint-dev-cromwell-execution/cromwell-executions/AdapterSmartSeq2SingleCell/workflow_id/call-analysis/SmartSeq2SingleCell/analysis_subworkflow_id/call-qc/RunHisat2Pipeline/qc_workflow_id/call-Hisat2/12345_qc.hisat2.met.txt'
        result = get_analysis_metadata.get_workflow_id(analysis_output_path)
        expected = 'analysis_subworkflow_id'
        self.assertEqual(result, expected)

    def test_get_auth(self):
        credentials_file = self.data_file('test_credentials.txt')
        auth = get_analysis_metadata.get_auth(credentials_file)
        expected_auth = HTTPBasicAuth('fake-user', 'fake-password')
        self.assertEqual(auth, expected_auth)

    @requests_mock.mock()
    @mock.patch('pipeline_tools.get_analysis_metadata.get_auth')
    def test_get_metadata_success(self, mock_request, mock_auth):
        def _request_callback(request, context):
            context.status_code = 200
            return {
                'workflowName': 'TestWorkflow'
            }
        mock_auth.return_value = HTTPBasicAuth('user', 'password')
        mock_request.get(self.cromwell_url, json=_request_callback)
        get_analysis_metadata.get_metadata(self.runtime_environment, self.workflow_id)
        self.assertEqual(mock_request.call_count, 1)

    @requests_mock.mock()
    @mock.patch('pipeline_tools.get_analysis_metadata.get_auth')
    def test_get_metadata_retries_on_failure(self, mock_request, mock_auth):
        def _request_callback(request, context):
            context.status_code = 500
            return {'status': 'error', 'message': 'Internal Server Error'}

        mock_auth.return_value = HTTPBasicAuth('user', 'password')
        # Makes the test complete faster by limiting the number of retries
        get_analysis_metadata.get_metadata.retry.stop = stop_after_attempt(3)

        mock_request.get(self.cromwell_url, json=_request_callback)

        with self.assertRaises(requests.HTTPError):
            get_analysis_metadata.get_metadata(self.runtime_environment, self.workflow_id)
            self.assertNotEqual(mock_request.call_count, 1)

        # Reset decorator default
        get_analysis_metadata.get_metadata.retry.stop = stop_after_delay(20)

    def data_file(self, file_name):
        return os.path.split(__file__)[0] + '/data/' + file_name


if __name__ == '__main__':
    unittest.main()