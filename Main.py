from Controller import Controller
from View import View


if __name__ == "__main__":
    ctrl = Controller.Controller()
    view = View.View(ctrl)
    view.run_view()
