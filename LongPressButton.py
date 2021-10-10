from kivy.base import runTouchApp
from kivy.clock import Clock
from kivy.factory import Factory


class LongpressButton(Factory.Button):
    __events__ = ('on_long_press',)
    background_down = 'src/btnPress.png'
    long_press_time = Factory.NumericProperty(1)
    font_size = 12
    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        pass