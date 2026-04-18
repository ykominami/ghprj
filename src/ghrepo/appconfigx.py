from typing import Any, ClassVar

from yklibpy.config.appconfig import AppConfig


class AppConfigx(AppConfig):
    """`ghrepo` 用の既定設定値と取得フィールドをまとめる。"""

    BASE_NAME_SNAPSHOTS: ClassVar[str] = "snapshots"  # スナップショット作成記録ファイルのベース名
    SNAPSHOT_TOP_DIR_NAME: ClassVar[str] = "snapshots"  # スナップショットトップディレクトリ名
    BASE_NAME_REPOS: ClassVar[str] = "repos"

    file_type_dict: ClassVar[dict[str, str]] = {
        AppConfig.FILE_TYPE_YAML: ".yaml",
        AppConfig.FILE_TYPE_JSON: ".json",
        AppConfig.FILE_TYPE_TOML: ".toml",
    }

    file_assoc: ClassVar[dict[str, dict[str, dict[str, Any]]]] = {
        AppConfig.KIND_CONFIG: {
            AppConfig.BASE_NAME_CONFIG: {
                AppConfig.FILE_TYPE: AppConfig.FILE_TYPE_YAML,
                AppConfig.EXT_NAME: "",
                AppConfig.PATH: {},
                AppConfig.VALUE: {},
            }
        },
        AppConfig.KIND_DB: {
            "repos": {
                AppConfig.FILE_TYPE: AppConfig.FILE_TYPE_YAML,
                AppConfig.EXT_NAME: "",
                AppConfig.PATH: {},
                AppConfig.VALUE: {},
            },
            "snapshots": {
                AppConfig.FILE_TYPE: AppConfig.FILE_TYPE_YAML,
                AppConfig.EXT_NAME: "",
                AppConfig.PATH: {},
                AppConfig.VALUE: {},
            },
        },
    }

    default_json_fields_in_db: ClassVar[list[str]] = [
        "name",
        "snapshot-id",
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
    default_json_fields: ClassVar[list[str]] = [
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
    key: ClassVar[str] = "JSON_FIELDS"
