class BrowserHistory:

    def __init__(self, homepage: str):
        self.stack_back=[]
        self.stack_foward=[]
        self.current=homepage
    def visit(self, url: str) -> None:
        if self.current:
            self.stack_back.append(self.current)
        self.stack_foward.clear()
        self.current=url

    def back(self, steps: int) -> str:
        while len(self.stack_back)>0 and steps>0:
            self.stack_foward.append(self.current)
            self.current=self.stack_back.pop(-1)
            steps=steps-1
        return self.current

    def forward(self, steps: int) -> str:
        while len(self.stack_foward)>0 and steps>0:
            self.stack_back.append(self.current)
            self.current=self.stack_foward.pop(-1)
            steps=steps-1
        return self.current


# Your BrowserHistory object will be instantiated and called as such:
# obj = BrowserHistory(homepage)
# obj.visit(url)
# param_2 = obj.back(steps)
# param_3 = obj.forward(steps)