#!/usr/bin/env python3


class Time(int):
    """Time is a unit of simulation steps. One step is 100ms"""

    pass


class Robot:
    pass


class Foo(int):
    """Each foo needs to have a unique id."""

    pass


class Bar(int):
    """Each bar needs to have a unique id."""

    pass


class Foobar:
    def __init__(self, foo: Foo, bar: Bar):
        self.foo = foo
        self.bar = bar


class Money(int):
    pass


class State:
    """State describes the simulated world."""

    def __init__(self):
        self.clock = Time(0)
        self.robots = [Robot(), Robot()]  # at the beginning, we have 2 robots
        self.foo_id = 0
        self.foos = []
        self.bar_id = 0
        self.bars = []
        self.foobars = []
        self.money = Money(0)
