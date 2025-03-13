class CurrentSourcePath:
    def __init__(self):
        self.path = None

    def get(self):
        return self.path

    def set(self, path):
        self.path = path
        self.path = self.path.replace("\\", "/")
        return self.path


current_source_path = CurrentSourcePath()
