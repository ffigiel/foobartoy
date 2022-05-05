#!/usr/bin/env python3

import random
from typing import List


class Time(int):
    """Time is a unit of simulation steps. One step is 100ms"""

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


class Robot:
    def __init__(self):
        self.action = RobotActionIdle()


class RobotAction:
    """Base class for all robot actions."""

    pass


class RobotActionIdle(RobotAction):
    """The robot has nothing to do."""

    pass


class RobotActionChangingTask(RobotAction):
    """Moving to change activity: occupy the robot for 5 seconds."""

    def __init__(self, next_task: RobotAction):
        self.remaining_time = Time(50)
        self.next_task = next_task


class RobotActionMiningFoo(RobotAction):
    """Mining foo: occupies the robot for 1 second."""

    def __init__(self):
        self.remaining_time = Time(10)


class RobotActionMiningBar(RobotAction):
    """Mining bar: keeps the robot busy for a random time between 0.5 and 2 seconds."""

    def __init__(self):
        random_ticks = round(random.random() * 15)
        self.remaining_time = Time(random_ticks + 5)


class RobotActionAssemblingFoobar(RobotAction):
    """Assembling a foobar from a foo and a bar: keeps the robot busy for 2 seconds."""

    def __init__(self, foo: Foo, bar: Bar):
        self.foo = foo
        self.bar = bar
        self.remaining_time = Time(20)


class RobotActionSellingFoobar(RobotAction):
    """Sell foobar: 10s to sell from 1 to 5 foobar."""

    def __init__(self, foobars: List[Foobar]):
        self.foobars = foobars
        self.remaining_time = Time(100)


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
