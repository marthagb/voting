#coding:utf-8
from copy import deepcopy
from apportion import apportion1d, threshold_elimination_constituencies

def norw_ice_apportionment(m_votes, v_total_seats, v_party_seats,
                            m_prior_allocations, divisor_gen, threshold=None,
                            orig_votes=None, **kwargs):
	m_allocations = deepcopy(m_prior_allocations)
	v_allocations = [sum(x) for x in zip(*m_allocations)]

	num_allocated = sum([sum(c) for c in m_allocations])
	total_seats = sum(v_total_seats)

	for n in range(total_seats-num_allocated):
		m_votes = threshold_elimination_constituencies(m_votes, 0.0,
                    v_party_seats, m_allocations)
		m_seat_props = []
		maximums = []
		for c in range(len(m_votes)):
			m_seat_props.append([])
			s = sum(orig_votes[c])
			for p in range(len(m_votes[c])):
				div = divisor_gen()
				for k in range(m_allocations[c][p]+1):
					x = next(div)
				if m_votes[c][p] != 0:
					a = (float(orig_votes[c][p])/s)*v_total_seats[c]/x
				else:
					a = 0
				m_seat_props[c].append(a)
			maximums.append(max(m_seat_props[c]))

			if sum(m_allocations[c]) == v_total_seats[c]:
				m_seat_props[c] = [0]*len(m_votes[c])
				maximums[c] = 0

		maximum = max(maximums)
		const = maximums.index(maximum)
		party = m_seat_props[const].index(maximum)

		m_allocations[const][party] += 1
		v_allocations[party] += 1


	return m_allocations, None
