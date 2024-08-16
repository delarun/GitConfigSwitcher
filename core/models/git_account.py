class GitAccount:
    name: str
    email: str
    gitname: str
    qAction: object

    def __init__(self, name: str, email: str, gitname: str) -> None:
        self.name = name
        self.email = email
        self.gitname = gitname