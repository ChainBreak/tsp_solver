class BaseSolver():
    def __next__(self):
        yield self()
    
    def __call__(self):
        raise NotImplementedError("A solver must implement the __call__ method")
