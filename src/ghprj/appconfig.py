class AppConfig:
    FILE_TYPE_YAML = "YAML"
    FILE_TYPE_JSON = "JSON"

    file_type_dict = {
        FILE_TYPE_YAML: ".yml",
        FILE_TYPE_JSON: ".json",
    }

    file_assoc = {
        "config": {
            "config": {
                "file_type": FILE_TYPE_YAML,
                "ext_name": "",
                "file": "",
                "value": "",
            }
        },
        "db": {
            "db": {
                "file_type": FILE_TYPE_YAML,
                "ext_name": "",
                "file": "",
                "value": "",
            },
            "fetch": {
                "file_type": FILE_TYPE_YAML,
                "ext_name": "",
                "file": "",
                "value": "",
            },
        },
    }
    default_json_fields_in_db = [
        "name",
        "count",
        "valid",
        "field_1",
        "field_2",
        "field_3",
        "url",
        "owner",
        "nameWithOwner",
        "parent",
        "pullRequests",
        "createdAt",
        "description",
        "diskUsage",
        "hasProjectsEnabled",
        "homepageUrl",
    ]
    default_json_fields = [
        "name",
        "url",
        "owner",
        "nameWithOwner",
        "parent",
        "pullRequests",
        "createdAt",
        "description",
        "diskUsage",
        "hasProjectsEnabled",
        "homepageUrl",
    ]
    fetch_item = {
        "date": "",
    }
    key = "JSON_FIELDS"
