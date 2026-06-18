``` mermaid
flowchart TB
    subgraph entry["エントリ"]
        init["__init__.py"]
        main["main()"]
        get_user["get_user()"]
    end

    subgraph ghrepo_pkg["ghrepo パッケージ"]
        Ghrepo["Ghrepo"]
        Clix["Clix"]
        AppConfigx["AppConfigx"]
        CommandSetup["CommandSetup"]
        CommandList["CommandList"]
        CommandSearch["CommandSearch"]
    end

    subgraph yklibpy["yklibpy"]
        AppConfig["AppConfig"]
        Cli["Cli"]
        Command["Command"]
        AppStore["AppStore"]
        CommandGhUser["CommandGhUser"]
        Loggerx["Loggerx"]
        Util["Util"]
        Storex["Storex"]
    end

    init --> Ghrepo
    init --> main
    init --> get_user
    main --> Ghrepo
    main --> Clix
    get_user --> CommandGhUser

    Ghrepo --> Clix
    Ghrepo --> AppConfigx
    Ghrepo --> CommandSetup
    Ghrepo --> CommandList
    Ghrepo --> CommandSearch
    Ghrepo --> AppStore
    Ghrepo --> CommandGhUser
    Ghrepo --> Loggerx
    Ghrepo --> Util
    Ghrepo --> Storex

    Clix --> Cli
    Clix -.-> AppConfigx

    AppConfigx --> AppConfig

    CommandSetup --> Command
    CommandSetup --> AppConfigx
    CommandSetup --> AppStore
    CommandSetup --> CommandGhUser
    CommandSetup --> Util

    CommandList --> Command
    CommandList --> AppConfigx
    CommandList --> AppStore
    CommandList --> Loggerx

    CommandSearch --> Command
    CommandSearch --> AppConfigx
    CommandSearch --> AppStore

    Cli -.-> CommandSetup
    Cli -.-> CommandList
    Cli -.-> CommandSearch

```
