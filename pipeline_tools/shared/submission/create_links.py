#!/usr/bin/env python
import argparse
import json
import os
import uuid

from pipeline_tools.shared.submission.format_map import NAMESPACE


def build_links(
    analysis_protocol_path,
    analysis_process_path,
    input_uuids,
    outputs_file_path,
    raw_schema_url,
    links_schema_version,
):
    """Create the submission envelope in Ingest service.

    Args:
        analysis_protocol_path (str): Path to the analysis_protocol json file.
        analysis_process_path (str): Path to the analysis_process json file.
        input_uuids (List[str]): List of UUIDs for the input files.
        outputs_file_path (str): Path to the outputs json file.
        raw_schema_url (str): URL prefix for retrieving HCA metadata schemas.
        links_schema_version (str): Version of the metadata schema that the links.json conforms to.
    """

    SCHEMA_TYPE = 'links'

    with open(analysis_protocol_path) as f:
        analysis_protocol_dict = json.load(f)

    with open(analysis_process_path) as f:
        analysis_process_dict = json.load(f)

    process_link = create_process_link(
        protocol_dict=analysis_protocol_dict,
        process_dict=analysis_process_dict,
        input_uuids=input_uuids,
        outputs_file_path=outputs_file_path,
    )

    links = {
        'describedBy': get_links_described_by(
            schema_url=raw_schema_url, schema_version=links_schema_version
        ),
        'schema_version': links_schema_version,
        'schema_type': SCHEMA_TYPE,
        'links': [process_link],
    }

    return links


def get_links_described_by(schema_url, schema_version):
    return f'{schema_url}/system/{schema_version}/links'


def create_process_link(protocol_dict, process_dict, input_uuids, outputs_file_path):
    LINK_TYPE = 'process_link'

    process_link = {
        'process_type': process_dict['describedBy'].split('/')[-1],
        'process_id': process_dict['process_core']['process_id'],
        'inputs': create_process_link_inputs(input_uuids),
        'outputs': create_process_link_outputs(outputs_file_path),
        'protocols': create_process_link_protocol(protocol_dict),
        'link_type': LINK_TYPE,
    }

    return process_link


def create_process_link_inputs(input_uuids):
    SEQUENCING_INPUT_TYPE = 'sequence_file'
    inputs = []

    for input_uuid in input_uuids:
        inputs.append({'input_type': SEQUENCING_INPUT_TYPE, 'input_id': input_uuid})

    return inputs


def create_process_link_outputs(outputs_file_path):
    outputs = []

    with open(outputs_file_path) as f:
        outputs_dict = json.load(f)

    for file_ref in outputs_dict:
        output_type = file_ref['describedBy'].split('/')[-1]
        output_id = file_ref['provenance']['document_id']

        outputs.append({'output_type': output_type, 'output_id': output_id})

    return outputs


def create_process_link_protocol(protocol_dict):
    protocols = []

    protocol_type = protocol_dict['type']['text']
    protocol_id = protocol_dict['provenance']['document_id']

    protocols.append({'protocol_type': protocol_type, 'protocol_id': protocol_id})

    return protocols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--analysis_process_path',
        required=True,
        help='Path to the analysis_process.json file.',
    )
    parser.add_argument(
        '--input_uuids', required=True, nargs='+', help='List of UUIDs.'
    )
    parser.add_argument(
        '--outputs_file_path', required=True, help='Path to the outputs.json file.'
    )
    parser.add_argument(
        '--analysis_protocol_path',
        required=True,
        help='Path to the analysis_protocol.json file.',
    )
    parser.add_argument(
        '--schema_url', required=True, help='URL for retrieving HCA metadata schemas.'
    )
    parser.add_argument(
        '--links_schema_version',
        required=True,
        help='The metadata schema version that the links files conform to.',
    )
    parser.add_argument('--project_id', required=True, help='The project ID')
    parser.add_argument(
        '--input_id',
        required=True,
        help='A unique input ID to incorporate into the links UUID.',
    )
    parser.add_argument(
        '--project_stratum_string',
        required=True,
        help="Concatenation of the project, library, species, and organ",
    )
    parser.add_argument(
        '--version',
        required=True,
        help='A version (or timestamp) attribute shared across all workflows'
        'within an individual workspace.',
    )
    args = parser.parse_args()

    schema_url = args.schema_url.strip('/')

    links = build_links(
        analysis_protocol_path=args.analysis_protocol_path,
        analysis_process_path=args.analysis_process_path,
        input_uuids=args.input_uuids,
        outputs_file_path=args.outputs_file_path,
        raw_schema_url=schema_url,
        links_schema_version=args.links_schema_version,
    )

    # Write links to file
    string_to_hash = f"{args.project_stratum_string}{args.input_id}"
    subgraph_uuid = uuid.uuid5(NAMESPACE, string_to_hash)

    if not os.path.exists("links"):
        os.mkdir("links")

    with open(f'links/{subgraph_uuid}_{args.version}_{args.project_id}.json', 'w') as f:
        json.dump(links, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
