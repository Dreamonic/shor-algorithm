class CircuitGui:
    def __init__(self, canvas):
        self.canvas = canvas
        self.circles = {}
        self.x_count = 0
        self.y_count = 0

    def draw_circle(self, x=0, y=0, r=1, **kwargs):
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def draw_circle_grid(self, x=0, y=0, x_count=0, y_count=0, width=5, height=5, r=1, **kwargs):
        x_offset = int((width - 2 * r - 2 * x) / (x_count - 1))
        y_offset = int((height - 2 * r - 2 * y) / (y_count - 1))

        for idx in range(x_count):
            for idy in range(y_count):
                self.circles[(idx, idy)] = (
                    self.draw_circle(x=x + r + x_offset * idx, y=y + r + y_offset * idy, r=r, **kwargs))
                self.set_inactive(idx, idy)

        self.x_count = x_count
        self.y_count = y_count
        return self.circles

    def draw_connection(self, c1: (int, int), c2: (int, int), **kwargs):
        x1, y1, x2, y2 = self.canvas.coords(self.circles[c1])
        r1 = (x2 - x1) / 2

        x3, y3, x4, y4 = self.canvas.coords(self.circles[c2])
        r2 = (x4 - x3) / 2
        l = self.canvas.create_line(x1 + r1, y1 + r1, x3 + r2, y3 + r2, **kwargs)
        self.canvas.tag_lower(l)

    def set_active(self, x, y, active_color='red'):
        self.canvas.itemconfig(self.circles[(x, y)], fill=active_color)

    def set_inactive(self, x, y, active_color='white'):
        self.canvas.itemconfig(self.circles[(x, y)], fill=active_color)

    def bus_line_connections(self, **kwargs):
        for y in range(self.y_count):
            self.draw_connection((0, y), (1, y), **kwargs)
            self.draw_connection((1, y), (2, y), **kwargs)
            if y > 0:
                self.draw_connection((1, y), (1, y - 1), **kwargs)
