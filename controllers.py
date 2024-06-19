class ViewController:
    def __init__(self, views):
        self.views = views
        self._current_view = 0
        self._current_subview = 0

    @property
    def home(self):
        return self._current_view == 0 and self._current_subview == 0

    def next_subview(self):
        view = self.views[self._current_view]
        if isinstance(view, tuple):
            self._current_subview += 1
            self._current_subview %= len(view)

    def next_view(self):
        if self._current_subview == 0:
            self._current_view += 1
            self._current_view %= len(self.views)
            self._current_subview = 0

    def prev_view(self):
        if self._current_subview == 0:
            self._current_view -= 1
            self._current_view %= len(self.views)
            self._current_subview = 0

    def get_current_view(self):
        view = self.views[self._current_view]
        return view[self._current_subview] if isinstance(view, tuple) else view

    @property
    def view(self):
        return self.get_current_view()

    def update(self):
        self.view.update()

    def render(self):
        self.view.render()

    def button_a(self):
        if not self.view.button_a():
            self.next_view()

    def button_b(self):
        self.view.button_b()

    def button_x(self):
        if not self.view.button_x():
            self.next_subview()
            return True
        return True

    def button_y(self):
        return self.view.button_y()
