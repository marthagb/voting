#coding:utf-8
"""
Command line interface for Voting.
"""
import click
import tabulate

import voting
import simulate as sim
import util
import web

### Monkey patching CSV output mode into tabulate:
tabulate.tabulate_formats.append("csv")
tabulate._table_formats["csv"] = tabulate.TableFormat(
    lineabove=None, linebelowheader=None, linebetweenrows=None,
    linebelow=None, headerrow=tabulate.DataRow(begin=u'', sep=u',', end=u''),
    datarow=tabulate.DataRow(begin=u'', sep=u',', end=u''),
    padding=0, with_header_hide=None)


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    """Basic CLI."""
    if debug:
        click.echo('Debug mode is on')


@cli.command()
@click.option('--votes', required=True, type=click.Path(exists=True),
              help='File with vote data to use as seed')
@click.option('--constituencies', required=True, type=click.Path(exists=True),
              help='File with constituency data')
@click.option('--num_sim', type=click.INT, default=10000,
              help='Number of simulations to run')
@click.option('--method', type=click.Choice(sim.GENERATING_METHODS.keys()),
              default="beta", help='Method to generate votes')
@click.option('--var_param', type=click.FLOAT, default=0.1)
def simulate(votes, constituencies, num_sim, method, var_param, **kwargs):
    """Simulate elections"""

    rules = voting.ElectionRules()
    rules["constituencies"] = constituencies
    parties, votes = util.load_votes(votes, rules["constituencies"])
    rules["parties"] = parties
    election = voting.Election(rules, votes)
    s_rules = sim.SimulationRules()
    s_rules["simulation_count"] = num_sim
    s_rules["simulation_variate"] = method
    simulation = sim.Simulation(s_rules, election, var_param)

    e_rules = []
    e_rules.append(voting.ElectionRules())
    e_rules[0]["constituency_seats"] = rules["constituency_seats"]
    e_rules[0]["constituency_adjustment_seats"] = rules["constituency_adjustment_seats"]
    e_rules[0]["constituency_names"] = rules["constituency_names"]
    e_rules[0]["parties"] = parties
    e_rules[0]["primary_divider"] = "dhondt"
    e_rules[0]["adjustment_divider"] = "dhondt"
    e_rules[0]["adjustment_threshold"] = 0.05
    e_rules[0]["adjustment_method"] = "icelandic-law"
    e_rules.append(voting.ElectionRules())
    e_rules[1]["constituency_seats"] = rules["constituency_seats"]
    e_rules[1]["constituency_adjustment_seats"] = rules["constituency_adjustment_seats"]
    e_rules[1]["constituency_names"] = rules["constituency_names"]
    e_rules[1]["parties"] = parties
    e_rules[1]["primary_divider"] = "sainte-lague"
    e_rules[1]["adjustment_divider"] = "sainte-lague"
    e_rules[1]["adjustment_threshold"] = 0.05
    e_rules[1]["adjustment_method"] = "icelandic-law"
    e_rules.append(voting.ElectionRules())
    e_rules[2]["constituency_seats"] = rules["constituency_seats"]
    e_rules[2]["constituency_adjustment_seats"] = rules["constituency_adjustment_seats"]
    e_rules[2]["constituency_names"] = rules["constituency_names"]
    e_rules[2]["parties"] = parties
    e_rules[2]["primary_divider"] = "dhondt"
    e_rules[2]["adjustment_divider"] = "dhondt"
    e_rules[2]["adjustment_threshold"] = 0.05
    e_rules[2]["adjustment_method"] = "relative-superiority"
    e_rules.append(voting.ElectionRules())
    e_rules[3]["constituency_seats"] = rules["constituency_seats"]
    e_rules[3]["constituency_adjustment_seats"] = rules["constituency_adjustment_seats"]
    e_rules[3]["constituency_names"] = rules["constituency_names"]
    e_rules[3]["parties"] = parties
    e_rules[3]["primary_divider"] = "sainte-lague"
    e_rules[3]["adjustment_divider"] = "sainte-lague"
    e_rules[3]["adjustment_threshold"] = 0.05
    e_rules[3]["adjustment_method"] = "relative-superiority"

    simulation.simulate(e_rules)

    # divider, adjustment_divider, constituencies, votes, voters,
    # simulations, threshold, betavariancesquared, partyweight, output,
    # adjustment_method

    # 1. Setup:
    #  - Load data files
    #  - Select methods
    # threshold *= 0.01
    # const = util.load_constituencies(constituencies)
    # parties, votes = util.load_votes(votes, const)
    #
    # divmethod = voting.DIVIDER_RULES[divider]
    # if not adjustment_divider:
    #     adjustment_divmethod = divmethod
    # else:
    #     adjustment_divmethod = voting.DIVIDER_RULES[adjustment_divider]
    #
    # for sim in range(simulations):
    #     print "\rSimulation %d" % sim,
    #     sys.stdout.flush()
    #
    #     for meth in adjustment_method:
    #         method = voting.ADJUSTMENT_METHODS[meth]
    #
    #         results = method(votes, v_const_seats, v_party_adjustment_seats,
    #                          m_allocations, adjustment_divmethod, threshold)

    # Output:
    #  - delta of entropy from optimal
    #  - delta of seats from optimal
    #  - smallest number of votes behind a seat
    #  - largest number of votes behind a seat
    #


@cli.command()
@click.option('--votes', required=True, type=click.Path(exists=True),
              help='File with vote data to use as seed')
@click.option('--consts', required=True, type=click.Path(exists=True),
              help='File with constituency data')
@click.option('--n', type=click.INT, default=10000,
              help='Number of simulations')
@click.option('--method', type=click.Choice(sim.GENERATING_METHODS.keys()),
              default="beta", help='Method to generate votes')
@click.option('--var_param', required=True, type=click.FLOAT, default=0.1)
def genvotes(votes, consts, n, method, var_param, output, **kwargs):
    rules = voting.ElectionRules()
    rules["constituencies"] = consts
    parties, votes = util.load_votes(votes, rules["constituencies"])
    rules["parties"] = parties
    election = voting.Election(rules, votes)
    s_rules = sim.SimulationRules()
    s_rules["simulation_count"] = n
    s_rules["simulation_variate"] = method
    simulation = sim.Simulation(s_rules, election, var_param)
    simulation.simulate([])


@cli.command()
@click.argument('rules', required=True,
                type=click.File('rb'))
def script(rules, **kwargs):
    """Read from a script file and execute its commands."""
    election = voting.run_script(rules)
    util.pretty_print_election(election.rules, election)


@cli.command()
@click.option('--host', required=False)
@click.option('--port', required=False, type=click.INT)
def www(host="localhost", port=5000, **kwargs):
    web.app.debug = True
    web.app.run(debug=True, host=host, port=port)


@cli.command()
@click.option('--divider', required=True,
              type=click.Choice(voting.DIVIDER_RULES.keys()),
              help='Divider rule to use.')
@click.option('--adjustment-divider', default=None, required=False,
              type=click.Choice(voting.DIVIDER_RULES.keys()),
              help='Divider rule for adjustment seats. Defaults to primary.')
@click.option('--constituencies', required=True, type=click.Path(exists=True),
              help='File with constituency data')
@click.option('--votes', required=True, type=click.Path(exists=True),
              help='File with vote data')
@click.option('--threshold', default=5,
              help='Threshold (in %%) for adjustment seats')
@click.option('--output', default='simple',
              type=click.Choice(tabulate.tabulate_formats))
@click.option('--show-entropy', default=False, is_flag=True)
@click.option('--adjustment-method', '-m',
              type=click.Choice(voting.ADJUSTMENT_METHODS.keys()),
              required=True)
@click.option('--show-constituency-seats', is_flag=True)
def apportion(votes, **kwargs):
    """Do regular apportionment based on votes and constituency data."""
    rules = voting.ElectionRules()
    kwargs["adjustment_divider"] = kwargs["adjustment_divider"] or kwargs["divider"]
    try:
      for arg, val in kwargs.iteritems():
        rules[arg] = val
    except AttributeError:
      for arg, val in kwargs.items():
        rules[arg] = val


    parties, votes = util.load_votes(votes, rules["constituencies"])
    rules["parties"] = parties
    election = voting.Election(rules, votes)
    election.run()

    util.pretty_print_election(rules, election)


if __name__ == '__main__':
    cli()
