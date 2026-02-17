from yklibpy.config.appconfig import AppConfig

class AppConfigx(AppConfig):
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
