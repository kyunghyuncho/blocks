from nose.tools import raises

from blocks.bricks import Bias, Linear, Sigmoid
from blocks.filter import VariableFilter
from blocks.graph import ComputationGraph
from blocks.roles import BIAS, FILTER, PARAMETER

from theano import tensor


def test_variable_filter():
    # Creating computation graph
    brick1 = Linear(input_dim=2, output_dim=2, name='linear1')
    brick2 = Bias(2, name='bias1')
    activation = Sigmoid(name='sigm')

    x = tensor.vector()
    h1 = brick1.apply(x)
    h2 = activation.apply(h1)
    y = brick2.apply(h2)
    cg = ComputationGraph(y)

    parameters = [brick1.W, brick1.b, brick2.params[0]]
    bias = [brick1.b, brick2.params[0]]
    brick1_bias = [brick1.b]

    # Testing filtering by role
    role_filter = VariableFilter(roles=[PARAMETER])
    assert parameters == role_filter(cg.variables)
    role_filter = VariableFilter(roles=[FILTER])
    assert [] == role_filter(cg.variables)

    # Testing filtering by role using each_role flag
    role_filter = VariableFilter(roles=[PARAMETER, BIAS])
    assert parameters == role_filter(cg.variables)
    role_filter = VariableFilter(roles=[PARAMETER, BIAS], each_role=True)
    assert not parameters == role_filter(cg.variables)
    assert bias == role_filter(cg.variables)

    # Testing filtering by bricks classes
    brick_filter = VariableFilter(roles=[BIAS], bricks=[Linear])
    assert brick1_bias == brick_filter(cg.variables)

    # Testing filtering by bricks instances
    brick_filter = VariableFilter(roles=[BIAS], bricks=[brick1])
    assert brick1_bias == brick_filter(cg.variables)

    # Testing filtering by brick instance
    brick_filter = VariableFilter(roles=[BIAS], bricks=[brick1])
    assert brick1_bias == brick_filter(cg.variables)

    # Testing filtering by name
    name_filter = VariableFilter(name='W_norm')
    assert [cg.variables[2]] == name_filter(cg.variables)

    # Testing filtering by name regex
    name_filter_regex = VariableFilter(name_regex='W_no.?m')
    assert [cg.variables[2]] == name_filter_regex(cg.variables)

    # Testing filtering by application
    appli_filter = VariableFilter(applications=[brick1.apply])
    variables = [cg.variables[1], cg.variables[8]]
    assert variables == appli_filter(cg.variables)

    # Testing filtering by application
    appli_filter_list = VariableFilter(applications=[brick1.apply])
    assert variables == appli_filter_list(cg.variables)


@raises(TypeError)
def test_variable_filter_roles_error():
    # Creating computation graph
    brick1 = Linear(input_dim=2, output_dim=2, name='linear1')

    x = tensor.vector()
    h1 = brick1.apply(x)
    cg = ComputationGraph(h1)
    # testing role error
    VariableFilter(roles=PARAMETER)(cg.variables)


@raises(TypeError)
def test_variable_filter_applications_error():
    # Creating computation graph
    brick1 = Linear(input_dim=2, output_dim=2, name='linear1')

    x = tensor.vector()
    h1 = brick1.apply(x)
    cg = ComputationGraph(h1)
    VariableFilter(applications=brick1.apply)(cg.variables)
