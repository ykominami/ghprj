from typing import Any, ClassVar

from yklibpy.config.appconfig import AppConfig


class AppConfigx(AppConfig):
    """`ghrepo` 用の既定設定値と取得フィールドをまとめる。"""

    # アプリケーション名
    APP_NAME: ClassVar[str] = "ghrepo"

    # ファイル・ディレクトリ名
    BASE_NAME_SNAPSHOTS: ClassVar[str] = "snapshots"
    SNAPSHOT_TOP_DIR_NAME: ClassVar[str] = "snapshots"
    BASE_NAME_REPOS: ClassVar[str] = "repos"
    SNAPSHOT_FILE_NAME: ClassVar[str] = "snapshot.yaml"

    # コンフィグキー
    KEY_USER: ClassVar[str] = "USER"
    key: ClassVar[str] = "JSON_FIELDS"

    # デフォルト数値
    DEFAULT_REPO_LIMIT: ClassVar[int] = 400
    LATEST_N: ClassVar[int] = 10

    # gh API フィールド名
    FIELD_NAME: ClassVar[str] = "name"
    FIELD_VISIBILITY: ClassVar[str] = "visibility"
    FIELD_URL: ClassVar[str] = "url"
    FIELD_OWNER: ClassVar[str] = "owner"
    FIELD_LOGIN: ClassVar[str] = "login"
    FIELD_NAME_WITH_OWNER: ClassVar[str] = "nameWithOwner"
    FIELD_PARENT: ClassVar[str] = "parent"
    FIELD_PULL_REQUESTS: ClassVar[str] = "pullRequests"
    FIELD_CREATED_AT: ClassVar[str] = "createdAt"
    FIELD_DESCRIPTION: ClassVar[str] = "description"
    FIELD_DISK_USAGE: ClassVar[str] = "diskUsage"
    FIELD_HAS_PROJECTS_ENABLED: ClassVar[str] = "hasProjectsEnabled"
    FIELD_HOMEPAGE_URL: ClassVar[str] = "homepageUrl"

    # 管理フィールド名
    FIELD_SNAPSHOT_ID: ClassVar[str] = "snapshot-id"
    FIELD_VALID: ClassVar[str] = "valid"
    FIELD_FIELD_1: ClassVar[str] = "field_1"
    FIELD_FIELD_2: ClassVar[str] = "field_2"
    FIELD_FIELD_3: ClassVar[str] = "field_3"

    # 公開種別・検索種別
    VISIBILITY_PUBLIC: ClassVar[str] = "public"
    VISIBILITY_PRIVATE: ClassVar[str] = "private"
    VISIBILITY_INTERNAL: ClassVar[str] = "internal"
    SEARCH_KIND_BOTH: ClassVar[str] = "both"
    SEARCH_KIND_LATEST10: ClassVar[str] = "latest10"

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
            BASE_NAME_REPOS: {
                AppConfig.FILE_TYPE: AppConfig.FILE_TYPE_YAML,
                AppConfig.EXT_NAME: "",
                AppConfig.PATH: {},
                AppConfig.VALUE: {},
            },
            BASE_NAME_SNAPSHOTS: {
                AppConfig.FILE_TYPE: AppConfig.FILE_TYPE_YAML,
                AppConfig.EXT_NAME: "",
                AppConfig.PATH: {},
                AppConfig.VALUE: {},
            },
        },
    }

    default_json_fields_in_db: ClassVar[list[str]] = [
        FIELD_NAME,
        FIELD_SNAPSHOT_ID,
        FIELD_VALID,
        FIELD_FIELD_1,
        FIELD_FIELD_2,
        FIELD_FIELD_3,
        FIELD_VISIBILITY,
        FIELD_URL,
        FIELD_OWNER,
        FIELD_NAME_WITH_OWNER,
        FIELD_PARENT,
        FIELD_PULL_REQUESTS,
        FIELD_CREATED_AT,
        FIELD_DESCRIPTION,
        FIELD_DISK_USAGE,
        FIELD_HAS_PROJECTS_ENABLED,
        FIELD_HOMEPAGE_URL,
    ]
    default_json_fields: ClassVar[list[str]] = [
        FIELD_NAME,
        FIELD_VISIBILITY,
        FIELD_URL,
        FIELD_OWNER,
        FIELD_NAME_WITH_OWNER,
        FIELD_PARENT,
        FIELD_PULL_REQUESTS,
        FIELD_CREATED_AT,
        FIELD_DESCRIPTION,
        FIELD_DISK_USAGE,
        FIELD_HAS_PROJECTS_ENABLED,
        FIELD_HOMEPAGE_URL,
    ]
