"""Closed ontology used by graph construction and claim validation."""

NODE_TYPES = {
    "service",
    "endpoint",
    "certificate",
    "algorithm",
    "software_component",
    "pipeline",
    "data_class",
    "device",
}

RELATION_SIGNATURES = {
    "HOSTS": {("service", "endpoint")},
    "PRESENTS": {("endpoint", "certificate")},
    "USES": {
        ("service", "algorithm"),
        ("service", "software_component"),
        ("certificate", "algorithm"),
        ("software_component", "algorithm"),
        ("device", "algorithm"),
    },
    "ISSUED_BY": {("certificate", "certificate")},
    "DEPENDS_ON": {
        ("service", "service"),
        ("service", "device"),
        ("software_component", "software_component"),
    },
    "DEPLOYS": {
        ("pipeline", "service"),
        ("pipeline", "device"),
    },
    "PROCESSES": {
        ("service", "data_class"),
        ("device", "data_class"),
    },
    "PROTECTS": {
        ("certificate", "data_class"),
        ("algorithm", "data_class"),
    },
}

# Only these paths may be collapsed into a derived USES assertion.
ALLOWED_PATH_RULES = {
    "hosted_certificate_algorithm": ("HOSTS", "PRESENTS", "USES"),
    "component_algorithm": ("USES", "USES"),
}

STRONG_IDENTIFIER_KEYS = {
    "fingerprint_sha256",
    "spki_sha256",
    "purl",
    "uid",
    "serial_number",
    "algorithm_id",
    "endpoint_uri",
    "pipeline_uid",
    "data_uid",
}

ALIAS_IDENTIFIER_KEYS = {
    "service_name",
    "hostname",
    "repository_path",
    "deployment_name",
}

