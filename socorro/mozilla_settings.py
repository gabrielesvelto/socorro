# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Settings for Mozilla's crash ingestion pipeline.
"""

import os
import socket
import tempfile

from everett.manager import ConfigManager, ListOf


_config = ConfigManager.basic_config()


LOCAL_DEV_ENV = _config(
    "LOCAL_DEV_ENV",
    default="False",
    parser=bool,
    doc="Whether or not this is a local development environment.",
)

HOST_ID = _config(
    "HOST_ID",
    default=socket.gethostname(),
    doc="Name of the host this is running on.",
)

ALWAYS_IGNORE_MISMATCHES = True

# Sentry DSN--leave as an empty string to disable
SENTRY_DSN = _config(
    "SENTRY_DSN", default="", doc="Sentry DSN or empty string to disable.",
)

# This has to be a valid level from the Python logging module
LOGGING_LEVEL = _config(
    "LOGGING_LEVEL",
    default="INFO",
    doc="Default logging level. Should be one of INFO, DEBUG, WARNING, ERROR.",
)

# Markus configuration for metrics
MARKUS_BACKENDS = [
    {
        "class": "markus.backends.statsd.StatsdMetrics",
        "options": {
            "statsd_host": _config(
                "STATSD_HOST", default="localhost", doc="statsd host.",
            ),
            "statsd_port": _config(
                "STATSD_PORT", default="8125", parser=int, doc="statsd port.",
            )
        },
    },
]
if LOCAL_DEV_ENV:
    MARKUS_BACKENDS.append({"class": "markus.backends.logging.LoggingMetrics"})

# Processor configuration
PROCESSOR = {
    "number_of_threads": _config(
        "PROCESSOR_NUMBER_OF_THREADS",
        default="4",
        parser=int,
        doc="Number of worker threads for the processor.",
    ),
    "maximum_queue_size": _config(
        "PROCESSOR_MAXIMUM_QUEUE_SIZE",
        default="8",
        parser=int,
        doc="Number of items to queue up from the processing queues.",
    ),
    "temporary_path": _config(
        "PROCESSOR_TEMPORARY_PATH",
        default=tempfile.gettempdir(),
        doc="Directory to use as a workspace for crash report processing.",
    ),
    "pipeline": {
        "class": "socorro.processor.processor_pipeline.ProcessorPipeline",
    },
}

# Crash report processing queue configuration
QUEUE = {
    "class": "socorro.external.sqs.crashqueue.SQSCrashQueue",
    "options": {
        "standard_queue": _config(
            "SQS_STANDARD_QUEUE",
            doc="Name for the standard processing queue.",
        ),
        "priority_queue": _config(
            "SQS_PRIORITY_QUEUE",
            doc="Name for the priority processing queue.",
        ),
        "reprocessing_queue": _config(
            "SQS_REPROCESSING_QUEUE",
            doc="Name for the reprocessing queue.",
        ),
        "access_key": _config("SQS_ACCESS_KEY", default="", doc="SQS access key."),
        "secret_access_key": _config(
            "SQS_SECRET_ACCESS_KEY",
            default="",
            doc="SQS secret access key.",
        ),
        "region": _config("SQS_REGION", default="", doc="SQS region."),

        "endpoint_url": _config(
            "SQS_ENDPOINT_URL",
            default="",
            doc=(
                "Endpoint url for AWS SQS. This is only used in the local dev "
                + "environment."
            ),
        ),
    },
}

# Crash report storage source
CRASH_SOURCE = {
    "class": "socorro.external.boto.crashstorage.BotoS3CrashStorage",
    "options": {
        "metrics_prefix": "processor.s3",
        "bucket_name": _config(
            "CRASHSTORAGE_S3_BUCKET_NAME",
            default="",
            doc="S3 bucket name for crash report data.",
        ),
        "access_key": _config(
            "CRASHSTORAGE_S3_ACCESS_KEY",
            default="",
            doc="S3 access key for crash report data.",
        ),
        "secret_access_key": _config(
            "CRASHSTORAGE_S3_SECRET_ACCESS_KEY",
            default="",
            doc="S3 secret access key for crash report data.",
        ),
        "region": _config(
            "CRASHSTORAGE_S3_REGION",
            default="",
            doc="S3 region for crash report data.",
        ),
        "endpoint_url": _config(
            "CRASHSTORAGE_S3_ENDPOINT_URL",
            default="",
            doc=(
                "Endpoint url for AWS S3 for crash report data. This is only used in "
                + "the local dev environment."
            ),
        ),
    },
}

# Each key in this list corresponds to a key in this dict containing a crash report data
# destination configuration
CRASH_DESTINATIONS_ORDER = ["s3", "elasticsearch", "statsd", "telemetry"]
CRASH_DESTINATIONS = {
    "s3": CRASH_SOURCE,
    "elasticsearch": {
        "class": "socorro.external.es.crashstorage.ESCrashStorage",
        "options": {
            "metrics_prefix": "processor.es",
            "index": "testsocorro%Y%W",
            "index_regex": "^testsocorro[0-9]{6}$",
            "urls": ["http://elasticsearch:9200"],
        },
    },
    "statsd": {
        "class": "socorro.external.crashstorage_base.MetricsCounter",
        "options": {
            "metrics_prefix": "processor",
        },
    },
    "telemetry": {
        "name": "telemetry",
        "class": "socorro.external.boto.crashstorage.TelemetryBotoS3CrashStorage",
        "options": {
            "metrics_prefix": "processor.telemetry",
            "bucket_name": _config(
                "TELEMETRY_S3_BUCKET_NAME",
                default="",
                doc="S3 bucket name for telemetry data export.",
            ),
            "access_key": _config(
                "TELEMETRY_S3_ACCESS_KEY",
                default="",
                doc="S3 access key for telemetry bucket.",
            ),
            "secret_access_key": _config(
                "TELEMETRY_S3_SECRET_ACCESS_KEY",
                default="",
                doc="S3 secret access key for telemetry bucket.",
            ),
            "region": _config(
                "TELEMETRY_S3_REGION",
                default="",
                doc="S3 region."),

            "endpoint_url": _config(
                "TELEMETRY_S3_ENDPOINT_URL",
                default="",
                doc=(
                    "Endpoint url for AWS S3 for the telemetry bucket. This is only "
                    + "used in the local dev environment."
                ),
            ),
        },
    },
}
SEARCH = CRASH_DESTINATIONS["elasticsearch"]

# Stackwalker configuration
STACKWALKER = {
    "command_path": _config(
        "STACKWALKER_COMMAND_PATH",
        default="/stackwalk-rust/minidump-stackwalk",
        doc="Aboslute path to the stackwalker binary.",
    ),
    "command_line": (
        "timeout --signal KILL {kill_timeout} "
        + "{command_path} "
        + "--evil-json={raw_crash_path} "
        + "--symbols-cache={symbol_cache_path} "
        + "--symbols-tmp={symbol_tmp_path} "
        + "--no-color "
        + "{symbols_urls} "
        + "--json "
        + "--verbose=error "
        + "{dump_file_path}"
    ),
    "dump_field": "upload_file_minidump",
    "kill_timeout": _config(
        "STACKWALKER_KILL_TIMEOUT",
        default="120",
        parser=int,
        doc="Timeout in seconds before the stackwalker is killed.",
    ),
    "symbols_urls": _config(
        "STACKWALKER_SYMBOLS_URLS",
        default="",
        parser=ListOf(str),
        doc="Comma-separated list of urls for symbols suppliers.",
    ),
    "symbol_cache_path": _config(
        "STACKWALKER_SYMBOLS_CACHE",
        default=os.path.join(tempfile.gettempdir(), "symbols", "cache"),
        doc="Directory to use for the on-disk LRU-cache for symbols files.",
    ),
    "symbol_tmp_path": _config(
        "STACKWALKER_SYMBOLS_TMP",
        default=os.path.join(tempfile.gettempdir(), "symbols", "tmp"),
        doc="Directory to use for temporary storage of files being downloaded.",
    ),
}

# Configuration for the symbols cache manager
SYMBOLS_CACHE_MANAGER = {
    "class": "socorro.processor.symbol_cache_manager.SymbolLRUCacheManager",
    "symbol_cache_size": "40G",
    "symbol_cache_path": STACKWALKER["symbol_cache_path"],
    "verbosity": 0,
}

BETAVERSIONRULE_VERSION_STRING_API = _config(
    "BETAVERSIONRULE_VERSION_STRING_API",
    default="https://crash-stats.mozilla.org/api/VersionString",
    doc="URL for the version string API endpoint in the Crash Stats webapp.",
)