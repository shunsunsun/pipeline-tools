from setuptools import setup


setup(
    name='pipeline-tools',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=['Programming Language :: Python :: 3'],
    description='Utilities for retrieving files from the HCA data storage service and submitting an analysis bundle '
    'to HCA-DCP',
    url='http://github.com/HumanCellAtlas/skylab',
    author='Human Cell Atlas Data Coordination Platform Mint Team',
    author_email='mintteam@broadinstitute.org',
    license='BSD 3-clause "New" or "Revised" License',
    packages=['pipeline_tools'],
    install_requires=[
        'arrow>=0.12.1',
        'google-auth>=1.6.1,<2',
        'google-cloud-storage>=1.10.0,<2',
        'hca>=7.0.0,<8',
        'mock>=2.0.0,<3',
        'requests>=2.20.0,<3',
        'requests-mock>=1.5.2,<2',
        'setuptools_scm>=2.0.0,<3',
        'tenacity>=4.10.0,<5',
        'PyJWT==1.6.4',
        'hca-metadata-api @ git+git://github.com/HumanCellAtlas/metadata-api@release/1.0b20',
    ],
    entry_points={
        'console_scripts': [
            'get-analysis-workflow-metadata=pipeline_tools.shared.submission.get_analysis_workflow_metadata:main',
            'create-analysis-metadata=pipeline_tools.shared.submission.create_analysis_metadata:main',
            'create-envelope=pipeline_tools.shared.submission.create_envelope:main',
            'create-file-descriptor=pipeline_tools.shared.submission.create_file_descriptor:main',
            'create-links=pipeline_tools.shared.submission.create_links:main',
            'create-reference-file=pipeline_tools.shared.submission.create_reference_file:main',
            'get-upload-urn=pipeline_tools.shared.submission.get_upload_urn:main',
            'get-files-to-upload=pipeline_tools.shared.submission.get_files_to_upload:main',
            'confirm-submission=pipeline_tools.shared.submission.confirm_submission:main',
        ]
    },
    include_package_data=True,
)
