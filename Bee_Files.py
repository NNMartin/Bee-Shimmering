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
        self.time_since_last_activation_pulse = refraction + act_length  # this just allows the bee to be active asap
        self.will_activate = will_activate  # This is really a shut off variable; look at update_pulse for more

    def update_pulse(self, activate=False):
        """
        :param bool activate: whether the bee has received a pulse to activate
        :return: None
        """
        # This is the main iteration function for the bee; ignores doing anything if the bee cannot be activated,
        # This speeds up the code a bit (and every bit helps)
        if self.will_activate:
            if activate and self.time_since_last_activation_pulse >= (self.refraction_period + self.activation_length):
                # This activates the bee; setting the time_since_last_activation_pulse to zero basically tells the bee
                # that it needs to start counting again
                self.is_active = True
                self.time_since_last_activation_pulse = 0
            elif self.is_active:
                if self.time_since_last_activation_pulse >= self.activation_length:
                    # This will trigger if the bee has already been active for its whole duration;
                    # at which point it will stop
                    self.is_active = False
                self.time_since_last_activation_pulse += 1  # This is because the next statement won't trigger
            elif self.time_since_last_activation_pulse < (self.refraction_period + self.activation_length):
                # There's really no point to have a value of time_since_last_activation_pulse higher than
                # refraction_period + activation_length
                self.time_since_last_activation_pulse += 1

    def is_it_active(self):
        """
        :return: bool
        """
        # This is because I dislike accessing of variables directly; It leads to bad programming practices and large
        # amounts of bugs; (sorry, my Java is showing)
        return self.is_active

    def activate(self):
        """ A dummy method to be overwritten
        :return: None
        """
        # This is for something that was originally scrapped, but might be useful later so I kept it in.
        pass

    def __str__(self):
        """ :return: str
        """
        if self.is_active:
            return "Active"
        else:
            return "Inactive"

    def __repr__(self):
        return str(self)


class GeneratorBee(Bee):
    """
    """
    def __init__(self, refraction, act_length, will_activate):
        """
        :param int refraction: length of refraction period in ticks
        :param int act_length: length of activation period in ticks
        """
        # will_activate is absolutely useless here; but because of the way subclasses work, we need it.
        Bee.__init__(self, refraction, act_length, will_activate=True)

    def activate(self):
        """
        :return: None
        """
        # Note an interesting fact here; the bee will activate even if it hasn't technically waited the whole period;
        # This is probably not true to nature, but from a programming perspective it was too potentially useful to not
        # allow.
        self.is_active = True
        self.time_since_last_activation_pulse = 0

