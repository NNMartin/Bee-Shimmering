"""
Version 1.0: March 9th, 2019
Bee: update pulse, activate; GeneratorBee: activate;
"""


class Bee:
    """
    :param bool is_active: Whether the bee is currently participating
    :param int refraction_period: how many ticks the bee must rest for between activations
    :param int activation_length: how many ticks the bee will remain active for
    :param int time_since_last_activation_pulse: the time since the bee last begun to be active
    :param bool will_activate: Whether the bee will even activate (outside of forcing by subclasses)
    """
    def __init__(self, refraction, act_length, will_activate):
        """
        :param int refraction: length of refraction period in ticks
        :param int act_length: length of activation period in ticks
        """
        self.is_active = False
        self.refraction_period = refraction
        self.activation_length = act_length
        self.time_since_last_activation_pulse = refraction + act_length
        self.will_activate = will_activate

    def update_pulse(self, activate=False):
        """
        :param bool activate: whether the bee has received a pulse to activate
        :return: None
        """
        if self.will_activate:
            if activate and self.time_since_last_activation_pulse >= (self.refraction_period + self.activation_length):
                self.is_active = True
                self.time_since_last_activation_pulse = 0
            elif self.is_active:
                if self.time_since_last_activation_pulse >= self.activation_length:
                    self.is_active = False
                self.time_since_last_activation_pulse += 1
            elif self.time_since_last_activation_pulse < (self.refraction_period + self.activation_length):
                self.time_since_last_activation_pulse += 1

    def is_it_active(self):
        """
        :return: bool
        """
        return self.is_active

    def activate(self):
        """ A dummy method to be overwritten
        :return: None
        """
        pass


class GeneratorBee(Bee):
    """
    """
    def __init__(self, refraction, act_length, will_activate):
        """
        :param int refraction: length of refraction period in ticks
        :param int act_length: length of activation period in ticks
        """
        Bee.__init__(self, refraction, act_length, will_activate=True)

    def activate(self):
        """
        :return: None
        """
        self.is_active = True
        self.time_since_last_activation_pulse = 0
