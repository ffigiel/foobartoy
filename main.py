#!/usr/bin/env python3

import random
from typing import List, Optional
from abc import ABCMeta


class Time:
    """Time is a unit of simulation steps. One step is 100ms"""

    def __init__(self, n):
        self.n = n

    def __lt__(self, other):
        return self.n.__lt__(other)

    def __gt__(self, other):
        return self.n.__gt__(other)

    def __eq__(self, other):
        return self.n.__eq__(other)

    def __str__(self) -> str:
        return f"{self.as_seconds()}€"

    def increment(self):
        self.n += 1

    def decrement(self):
        self.n -= 1

    def as_seconds(self) -> float:
        return float(self.n) / 10


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


class Money:
    """Money is a unit of currency in the simulation."""

    def __init__(self, n):
        self.n = n

    def __str__(self) -> str:
        return f"{self.n}€"

    def add(self, n: int):
        self.n += n

    def sub(self, n: int):
        self.n -= n


class RobotAction(metaclass=ABCMeta):
    """Base class for all robot actions."""

    remaining_time = Time(0)


class RobotActionIdle(RobotAction):
    """The robot has nothing to do."""

    def __init__(self, prev_action: Optional[RobotAction]):
        self.prev_action = prev_action


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


class RobotActionSellingFoobars(RobotAction):
    """Sell foobar: 10s to sell from 1 to 5 foobar."""

    def __init__(self, foobars: List[Foobar]):
        self.foobars = foobars
        self.remaining_time = Time(100)


class Robot:
    action: RobotAction

    def __init__(self):
        self.action = RobotActionIdle(None)


class State:
    """State describes the simulated world."""

    def __init__(self):
        self.clock = Time(0)
        self.robots = [Robot(), Robot()]  # at the beginning, we have 2 robots
        self.foo_ctr = 0
        self.foos = []
        self.bar_ctr = 0
        self.bars = []
        self.foobars = []
        self.money = Money(0)


def main():
    state = State()
    print("infinite loop")
    while True:
        update_current_robot_actions(state)
        # state = buy_more_robots_if_possible(state)
        if len(state.robots) >= 30:
            print(f"Finished with {len(state.robots)} robots in {state.clock}s.")
            break
        state.clock.increment()


def update_current_robot_actions(state: State) -> State:
    for robot in state.robots:
        robot.action.remaining_time.decrement()
        if robot.action.remaining_time > 0:
            continue
        # Action is finished
        if isinstance(robot.action, RobotActionChangingTask):
            robot.action = robot.action.next_task
        elif isinstance(robot.action, RobotActionMiningFoo):
            state = create_foo(state)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionMiningBar):
            state = create_bar(state)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionAssemblingFoobar):
            state = create_bar(state)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionSellingFoobars):
            state = sell_foobars(state, robot.action.foobars)
            robot.action = RobotActionIdle(robot.action)
    return state


def create_foo(state: State) -> State:
    state.foo_ctr += 1
    state.foos.append(Foo(state.foo_ctr))
    return state


def create_bar(state: State) -> State:
    state.bar_ctr += 1
    state.bars.append(Bar(state.bar_ctr))
    return state


def assemble_foobar(state: State, foo: Foo, bar: Bar) -> State:
    if random.random() < 0.6:
        # The operation has a 60% chance of success
        foobar = Foobar(foo, bar)
        state.foobars.append(foobar)
    else:
        # in case of failure the bar can be reused, the foo is lost.
        state.bars.append(bar)
    return state


def sell_foobars(state: State, foobars: List[Foobar]) -> State:
    # we earn €1 per foobar sold
    state.money.add(len(foobars))
    return state


if __name__ == "__main__":
    main()
