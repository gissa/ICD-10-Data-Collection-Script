# ICD-10 Data Collection Script

This Python script fetches and saves data for ICD-10 codes from the World Health Organization (WHO) API.
It traverses the entire ICD-10 hierarchy, saving each code's data as a separate JSON file.

## Features

- Configurable via command-line arguments or a config file
- Comprehensive error handling and logging
- Respects API rate limits with configurable delays
- Resumable: can continue from where it left off if interrupted

## Prerequisites

- Python 3.6 or higher
- `requests` library
- https://icd.who.int/icdapi Account to generate TOKEN

## Installation

1. Fork and clone this repository:
   ```
   git clone https://github.com/your-username/icd10-data-collection.git
   cd icd10-data-collection
   ```

2. Install the required library:
   ```
   pip install requests
   ```

## Usage

Run the script with:

```
python icd_api_request.py [options]
```

### Options

- `--token TOKEN`: Bearer token for API authentication (required)
- `--output-dir DIR`: Directory to save the JSON files (default: icd_data)
- `--delay SECONDS`: Delay between API requests in seconds (default: 0.5)
- `--log-file FILE`: Log file path (default: icd_api.log)
- `--config-file FILE`: Path to a configuration file. If you don't have a token,
                        you can provide client_id and client_secret in a config file.

### Configuration File

You can use a configuration file instead of command-line arguments. Create a file named `config.ini` with the following structure:

```ini
[DEFAULT]
token = your_bearer_token_here
output_dir = icd_data
delay = 0.5
log_file = icd_api.log
client_id = 'xxxx'
client_secret = 'aaaa'
```

Then run the script with:

```
python icd_api_request.py --config-file config.ini
```

## Output

The script will create a directory (default: `icd_data`) and save each ICD-10 code's data as a separate JSON file within this directory. The files are named according to the ICD-10 code, with dots and slashes replaced by underscores.

## Logging

The script logs its progress to both the console and a log file (default: `icd_api.log`). Check this file for detailed information about the script's execution.

## Rate Limiting

To avoid overwhelming the WHO API, the script includes a configurable delay between requests (default: 0.5 seconds). Adjust this value using the `--delay` option if you encounter rate limiting issues.

## Error Handling

The script includes error handling for API requests and file operations. If an error occurs while fetching or saving data for a specific code, the script will log the error and continue with the next code.

## Resuming Interrupted Execution

If the script is interrupted, you can simply run it again with the same configuration. It will skip over codes that have already been saved, allowing you to resume the data collection process.

## Contributing

Contributions to improve the script are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This script is for educational and research purposes only. Ensure that your use of the WHO API complies with their terms of service and data usage policies.
