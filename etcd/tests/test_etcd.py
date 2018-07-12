# (C) Datadog, Inc. 2018
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import pytest

from datadog_checks.etcd import Etcd


CHECK_NAME = 'etcd'

STORE_METRICS = [
    'compareanddelete.fail',
    'compareanddelete.success',
    'compareandswap.fail',
    'compareandswap.success',
    'create.fail',
    'create.success',
    'delete.fail',
    'delete.success',
    'expire.count',
    'gets.fail',
    'gets.success',
    'sets.fail',
    'sets.success',
    'update.fail',
    'update.success',
    'watchers',
]


def test_bad_config(aggregator):
    instance = {'url': 'http://localhost:2379/test'}
    check = Etcd(CHECK_NAME, None, {}, [instance])

    with pytest.raises(Exception):
        check.check(instance)

    aggregator.assert_service_check(check.SERVICE_CHECK_NAME, tags=['url:http://localhost:2379/test'], count=1)
    aggregator.assert_service_check(check.HEALTH_SERVICE_CHECK_NAME)


def test_metrics(main_instance, aggregator):
    check = Etcd(CHECK_NAME, None, {}, [main_instance])
    check.check(main_instance)

    tags = ['url:http://localhost:2379', 'etcd_state:leader']

    for mname in STORE_METRICS:
        aggregator.assert_metric('etcd.store.{}'.format(mname), tags=tags, count=1)

    aggregator.assert_metric('etcd.self.send.appendrequest.count', tags=tags, count=1)
    aggregator.assert_metric('etcd.self.recv.appendrequest.count', tags=tags, count=1)


def test_service_checks(main_instance, aggregator):
    check = Etcd(CHECK_NAME, None, {}, [main_instance])
    check.check(main_instance)

    tags = ['url:http://localhost:2379', 'etcd_state:leader']

    aggregator.assert_service_check(check.SERVICE_CHECK_NAME, tags=tags, count=1)
    aggregator.assert_service_check(check.HEALTH_SERVICE_CHECK_NAME, tags=tags[:1], count=1)


# FIXME: not really an integration test, should be pretty easy
# to spin up a cluster to test that.
def test_followers(self):
    mock = {
        "followers": {
            "etcd-node1": {
                "counts": {
                    "fail": 1212,
                    "success": 4163176
                },
                "latency": {
                    "average": 2.7206299430775007,
                    "current": 1.486487,
                    "maximum": 2018.410279,
                    "minimum": 1.011763,
                    "standardDeviation": 6.246990702203536
                }
            },
            "etcd-node3": {
                "counts": {
                    "fail": 1378,
                    "success": 4164598
                },
                "latency": {
                    "average": 2.707100125761001,
                    "current": 1.666258,
                    "maximum": 1409.054765,
                    "minimum": 0.998415,
                    "standardDeviation": 5.910089773061448
                }
            }
        },
        "leader": "etcd-node2"
    }

    mocks = {
        '_get_leader_metrics': lambda url, path, ssl, timeout: mock
    }

    self.run_check_twice(self.config, mocks=mocks)

    common_leader_tags = ['url:http://localhost:2379', 'etcd_state:leader']
    follower_tags = [
        common_leader_tags[:] + ['follower:etcd-node1'],
        common_leader_tags[:] + ['follower:etcd-node3'],
    ]

    for fol_tags in follower_tags:
        self.assertMetric('etcd.leader.counts.fail', count=1, tags=fol_tags)
        self.assertMetric('etcd.leader.counts.success', count=1, tags=fol_tags)
        self.assertMetric('etcd.leader.latency.avg', count=1, tags=fol_tags)
        self.assertMetric('etcd.leader.latency.min', count=1, tags=fol_tags)
        self.assertMetric('etcd.leader.latency.max', count=1, tags=fol_tags)
        self.assertMetric('etcd.leader.latency.stddev', count=1, tags=fol_tags)
        self.assertMetric('etcd.leader.latency.current', count=1, tags=fol_tags)
