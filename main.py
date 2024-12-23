"""
ICD-10 Data Collection Script

This script fetches and saves data for ICD-10 codes from the WHO API.
It traverses the entire ICD-10 hierarchy, saving each code's data as a separate JSON file.

Features:
- Configurable via command-line arguments or a config file
- Comprehensive error handling and logging
- Respects API rate limits with configurable delays
- Resumable: can continue from where it left off if interrupted

Usage:
python icd_api_request.py [options]

Options:
  --token TOKEN        Bearer token for API authentication
  --output-dir DIR     Directory to save the JSON files (default: icd_data)
  --delay SECONDS      Delay between API requests in seconds (default: 0.5)
  --log-file FILE      Log file path (default: icd_api.log)
  --config-file FILE   Path to a configuration file. If you don't have a token,
                       you can provide client_id and client_secret in a config file.

For more information, see the README.md file.
"""
from pathlib import Path

import requests
import json
import os
import time
import logging
import argparse
from urllib.parse import unquote
from configparser import ConfigParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config():
    parser = argparse.ArgumentParser(description="Fetch and save ICD-10 data from WHO API")
    parser.add_argument("--token", help="Bearer token for API authentication")
    parser.add_argument("--output-dir", default="icd_data", help="Directory to save the JSON files")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between API requests in seconds")
    parser.add_argument("--log-file", default="icd_api.log", help="Log file path")
    parser.add_argument("--config-file", help="Path to a configuration file")
    
    args = parser.parse_args()
    
    if args.config_file:
        config = ConfigParser()
        config.read(args.config_file)
        defaults = dict(config['DEFAULT'])
        if not defaults.get('token'):
            token = get_token_from_icd_api(defaults['client_id'], defaults['client_secret'])
            defaults['token'] = token
        parser.set_defaults(**defaults)
        args = parser.parse_args()  # re-parse args to override with config file values

    if not args.token:
        raise Exception("Please provide a token or a config file with client_id and client_secret")
    return args


def get_token_from_icd_api(client_id, client_secret):
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'icdapi_access',
        'grant_type': 'client_credentials'
    }
    response = requests.post(
        'https://icdaccessmanagement.who.int/connect/token',
        data=payload,
        verify=False
    )
    if response.ok:
        response = response.json()
        return response['access_token']
    return


def fetch_icd_data(code, token):
    url = f'https://id.who.int/icd/release/10/2010/{code}'
    headers = {
        'accept': 'application/json',
        'API-Version': 'v2',
        'Accept-Language': 'en',
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data for code {code}: {str(e)}")
        return None


def save_icd_data(data, code, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = os.path.join(output_dir, f'icd10_{code.replace(".", "_").replace("/", "_")}.json')
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data for code {code} saved to {filename}")
    except IOError as e:
        logger.error(f"Error saving data for code {code}: {str(e)}")


def process_icd_code(code, config, existing_codes=None):
    logger.info(f"Fetching data for ICD-10 code: {code}")

    potential_name = f'icd10_{code.replace(".", "_").replace("/", "_")}.json'
    if existing_codes and potential_name in existing_codes:
        logger.info(f"Code {code} already exists ({potential_name}). Skipping.")
        return
    else:
        data = fetch_icd_data(code, config.token)

    if data:
        save_icd_data(data, code, config.output_dir)
        
        if 'child' in data:
            for child_url in data['child']:
                child_code = unquote(child_url.split('/')[-1])
                process_icd_code(child_code, config, existing_codes=existing_codes)
    
    time.sleep(config.delay)


def get_root_codes(token):
    root_data = fetch_icd_data('', token)
    if isinstance(root_data, dict) and 'child' in root_data:
        return [unquote(url.split('/')[-1]) for url in root_data['child']]
    else:
        logger.warning("Error fetching root codes. Using default list.")
        return ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX', 'XXI', 'XXII']


def main():
    config = load_config()
    
    # Set up file logging
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    logger.info("Starting ICD-10 data collection")
    
    root_codes = get_root_codes(config.token)
    logger.info(f"Root codes: {root_codes}")

    existing_codes = None
    if config.check_existing:
        directory = Path(config.output_dir)
        existing_codes = [f.name for f in directory.iterdir() if f.is_file() and f.name.endswith('.json')]
        logger.info(f"There are {len(existing_codes)} existing codes")

    for code in root_codes:
        process_icd_code(code, config, existing_codes=existing_codes)

    logger.info("Data collection and saving complete.")


if __name__ == "__main__":
    main()
