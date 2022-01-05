from behave import *
from twentyone import *

@given ("a dealer")
def setp_impl (context):
    context.dealer = Dealer()

@when ("the round starts")
def step_impl (context):
    context.dealer.new_round()

@then ("The dealer gives itself two cards")
def step_impl (context):
    assert len(context.dealer.hand) == 2, f"The dealer should have 2 cards by now, but only has {len(context.dealer.hand)}"