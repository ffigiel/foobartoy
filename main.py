#!/usr/bin/env python3

from __future__ import annotations

import random
from typing import List, Optional, Type
from abc import ABCMeta


class Time:
    """Time is a unit of simulation steps. One step is 100ms"""

    def __init__(self, n):
        self.n = n

    def __lt__(self, other: Time):
        return self.n.__lt__(other.n)

    def __gt__(self, other: Time):
        return self.n.__gt__(other.n)

    def __eq__(self, other: Time):
        return self.n.__eq__(other.n)

    def __str__(self) -> str:
        return f"{self.as_seconds()}s"

    def increment(self):
        self.n += 1

    def decrement(self):
        self.n -= 1

    def as_seconds(self) -> float:
        return float(self.n) / 10


class Foo(int):
    """Each foo must have a unique serial number."""

    def __repr__(self) -> str:
        return f"foo_{int(self)}"


class Bar(int):
    """Each bar must have a unique serial number."""

    def __repr__(self) -> str:
        return f"bar_{int(self)}"


class Foobar:
    def __init__(self, foo: Foo, bar: Bar):
        self.foo = foo
        self.bar = bar

    def __str__(self) -> str:
        return f"foobar_{int(self.foo)}_{int(self.bar)}"


class Money:
    """Money is a unit of currency in the simulation."""

    def __init__(self, n):
        self.n = n

    def __lt__(self, other: Money):
        return self.n.__lt__(other.n)

    def __gt__(self, other: Money):
        return self.n.__gt__(other.n)

    def __eq__(self, other: Money):
        return self.n.__eq__(other.n)

    def __str__(self) -> str:
        return f"{self.n}€"

    def add(self, other: Money):
        self.n += other.n

    def sub(self, other: Money):
        self.n -= other.n


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
    """Assembling a foobar from a foo and a bar: keeps the robot busy for 2 seconds.

    The operation has a 60% chance of success.
    """

    success_chance = 0.6

    def __init__(self, foo: Foo, bar: Bar):
        self.foo = foo
        self.bar = bar
        self.remaining_time = Time(20)


class RobotActionSellingFoobars(RobotAction):
    """Sell foobar: 10s to sell from 1 to 5 foobar."""

    max_foobars = 5

    def __init__(self, foobars: List[Foobar]):
        if len(foobars) > self.max_foobars:
            raise ValueError(f"Cannot sell more than {self.max_foobars} foobars.")
        self.foobars = foobars
        self.remaining_time = Time(100)

    @property
    def profit(self):
        # we earn €1 per foobar sold
        return Money(len(self.foobars))


class RobotActionBuyNewRobot(RobotAction):
    """Buy a new robot for €3 and 6 foo, 0s"""

    cost = Money(3)
    foos_required = 6

    def __init__(self, foos: List[Foo]):
        if len(foos) != self.foos_required:
            raise ValueError(f"Need {self.foos_required} foos to buy a robot.")
        self.foos = foos
        self.remaining_time = Time(100)


class Robot:
    action: RobotAction

    def __init__(self):
        self.action = RobotActionIdle(None)

    def set_action(self, action: RobotAction):
        if self.action.remaining_time > Time(0):
            raise ValueError("This robot is busy and cannot do this action.")
        if robot_did_this_action_recently(self, type(action)):
            self.action = action
        else:
            self.action = RobotActionChangingTask(action)


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


class FutureState:
    """State we expect to have in the future."""

    def __init__(self, state):
        self.num_foos = len(state.foos)
        self.num_bars = len(state.bars)
        self.num_foobars = len(state.foobars)
        self.money = state.money
        for robot in state.robots:
            action = robot.action
            if isinstance(action, RobotActionChangingTask):
                action = action.next_task
            if isinstance(action, RobotActionMiningFoo):
                self.num_foos += 1
            elif isinstance(action, RobotActionMiningBar):
                self.num_bars += 1
            elif isinstance(action, RobotActionAssemblingFoobar):
                self.num_foobars += action.success_chance
                self.num_bars += 1 - action.success_chance
            elif isinstance(action, RobotActionSellingFoobars):
                self.money.add(action.profit)


def main():
    state = State()
    while True:
        state = update_robot_actions_progress(state)
        state = dispatch_robot_actions(state)
        if len(state.robots) >= 30:
            print(f"Finished with {len(state.robots)} robots in {state.clock}.")
            break
        state.clock.increment()


def update_robot_actions_progress(state: State) -> State:
    for robot in state.robots:
        robot.action.remaining_time.decrement()
        if robot.action.remaining_time > Time(0):
            continue
        # Action is finished
        if isinstance(robot.action, RobotActionChangingTask):
            robot.action = robot.action.next_task
            # Need to check remaining time again, for example buying a new robot takes 0s to complete
            if robot.action.remaining_time > Time(0):
                continue
        if isinstance(robot.action, RobotActionMiningFoo):
            state = mine_foo(state)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionMiningBar):
            state = mine_bar(state)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionAssemblingFoobar):
            state = assemble_foobar(state, robot.action)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionSellingFoobars):
            state = sell_foobars(state, robot.action)
            robot.action = RobotActionIdle(robot.action)
        elif isinstance(robot.action, RobotActionBuyNewRobot):
            state = buy_new_robot(state, robot.action)
            robot.action = RobotActionIdle(robot.action)
    return state


def mine_foo(state: State) -> State:
    state.foo_ctr += 1
    foo = Foo(state.foo_ctr)
    state.foos.append(foo)
    print(f"mined {foo}")
    return state


def mine_bar(state: State) -> State:
    state.bar_ctr += 1
    bar = Bar(state.bar_ctr)
    state.bars.append(bar)
    print(f"mined {bar}")
    return state


def assemble_foobar(state: State, action: RobotActionAssemblingFoobar) -> State:
    if random.random() < action.success_chance:
        foobar = Foobar(action.foo, action.bar)
        print(f"assembled {foobar}")
        state.foobars.append(foobar)
    else:
        # in case of failure the bar can be reused, the foo is lost.
        print(f"assembling foobar failed, recovered {action.bar}")
        state.bars.append(action.bar)
    return state


def sell_foobars(state: State, action: RobotActionSellingFoobars) -> State:
    print(f"sold {action.foobars} for {action.profit}")
    state.money.add(action.profit)
    return state


def buy_new_robot(state: State, action: RobotActionBuyNewRobot) -> State:
    print(f"bought a new robot for {action.cost} and {action.foos}")
    state.robots.append(Robot())
    return state


def dispatch_robot_actions(state: State) -> State:
    for robot in state.robots:
        if not isinstance(robot.action, RobotActionIdle):
            continue
        # This robot is idle
        # Prioritize buying more robots whenever possible
        if can_afford_new_robot(state):
            if should_this_robot_do_that_action(state, robot, RobotActionBuyNewRobot):
                state = go_buy_new_robot(state, robot)
                continue
        # Always sell maximum amount of foobars to save time
        if len(state.foobars) >= RobotActionSellingFoobars.max_foobars:
            if should_this_robot_do_that_action(
                state, robot, RobotActionSellingFoobars
            ):
                state = go_sell_foobars(state, robot)
                continue
        # See what resources will be available in the future
        future_state = FutureState(state)
        # Assemble foobars if we have surplus resources
        if (
            len(state.foos) > RobotActionBuyNewRobot.foos_required
            and len(state.bars) > 0
        ):
            if should_this_robot_do_that_action(
                state, robot, RobotActionAssemblingFoobar
            ):
                state = go_assemble_foobars(state, robot)
                continue
        # Mine foos/bars based on which we need more of
        fb_diff = future_state.num_foos - future_state.num_bars
        if fb_diff < RobotActionBuyNewRobot.foos_required:
            state = go_mine_foos(state, robot)
            continue
        else:
            state = go_mine_bars(state, robot)
            continue
    return state


def can_afford_new_robot(state: State) -> bool:
    return (state.money > RobotActionBuyNewRobot.cost) and (
        len(state.foos) > RobotActionBuyNewRobot.foos_required
    )


def should_this_robot_do_that_action(
    state: State, robot: Robot, action: Type[RobotAction]
) -> bool:
    # Can I do it efficiently?
    if robot_did_this_action_recently(robot, action):
        return True
    # Can other robot do it for me?
    for other_robot in state.robots:
        if other_robot != robot and robot_did_this_action_recently(other_robot, action):
            return False
    # The robots are busy with other things, I must do the task myself.
    return True


def robot_did_this_action_recently(robot: Robot, action: Type[RobotAction]) -> bool:
    return isinstance(robot.action, RobotActionIdle) and isinstance(
        robot.action.prev_action, action
    )


def go_buy_new_robot(state: State, robot: Robot) -> State:
    state.money.sub(RobotActionBuyNewRobot.cost)
    fr = RobotActionBuyNewRobot.foos_required
    foos, state.foos = state.foos[:fr], state.foos[fr:]
    action = RobotActionBuyNewRobot(foos)
    robot.set_action(action)
    print(f"buying a new robot for {action.cost} and {action.foos}")
    return state


def go_sell_foobars(state: State, robot: Robot) -> State:
    mf = RobotActionSellingFoobars.max_foobars
    foobars, state.foobars = state.foobars[:mf], state.foobars[mf:]
    action = RobotActionSellingFoobars(foobars)
    robot.set_action(action)
    print(f"selling {action.foobars} for {action.profit}")
    return state


def go_assemble_foobars(state: State, robot: Robot) -> State:
    foo = state.foos.pop()
    bar = state.bars.pop()
    action = RobotActionAssemblingFoobar(foo, bar)
    robot.set_action(action)
    print(f"assembling foobar with {foo} and {bar}")
    return state


def go_mine_foos(state: State, robot: Robot) -> State:
    action = RobotActionMiningFoo()
    robot.set_action(action)
    print(f"mining a foo")
    return state


def go_mine_bars(state: State, robot: Robot) -> State:
    action = RobotActionMiningBar()
    robot.set_action(action)
    print(f"mining a bar")
    return state


if __name__ == "__main__":
    main()
