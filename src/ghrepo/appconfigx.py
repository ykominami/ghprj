from yklibpy.config.appconfig import AppConfig


class AppConfigx(AppConfig):
    """`ghrepo` 用の既定設定値と取得フィールドをまとめる。"""

    default_json_fields_in_db: list[str] = [
        "name",
        "count",
        "valid",
        "field_1",
        "field_2",
        "field_3",
        "visibility",
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
    default_json_fields: list[str] = [
        "name",
        "visibility",
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
    key: str = "JSON_FIELDS"
